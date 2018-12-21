/*
 * Copyright 2018 Alexander Fasching
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "cpu/pred/external_bp.hh"

#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#include <cstdio>

#define BUFSIZE 1024

#define METH_UNCOND_BRANCH  0
#define METH_LOOKUP         1
#define METH_BTB_UPDATE     2
#define METH_UPDATE         3
#define METH_SQUASH         4


struct __attribute__((packed)) {
  uint8_t method_id;
  int16_t tid;
  uint64_t branch_addr;
  uint64_t bp_history_index;
  uint8_t taken;
  uint8_t squashed;
} msg_buffer;

struct __attribute__((packed)) {
  uint8_t pred;
  uint64_t bp_history_index;
} rsp_buffer;


ExternalBP::ExternalBP(const ExternalBPParams *params)
    : BPredUnit(params)
{
  struct sockaddr_un addr;
  memset(&addr, 0, sizeof(addr));
  addr.sun_family = AF_UNIX;
  const char *socketName = params->socketName.c_str();
  strncpy(addr.sun_path, socketName, sizeof(addr.sun_path) - 1);

  int connfd = socket(AF_UNIX, SOCK_STREAM, 0);
  assert(connect(connfd, (struct sockaddr *) &addr, sizeof(addr)) == 0);
  connfp = fdopen(connfd, "r+");
}


void
ExternalBP::btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history)
{
  errno = 0;
  msg_buffer.method_id = METH_BTB_UPDATE;
  msg_buffer.tid = tid;
  msg_buffer.branch_addr = branch_addr;
  msg_buffer.bp_history_index = (uint64_t) bp_history;

  fwrite(&msg_buffer, sizeof(msg_buffer), 1, connfp);
  fflush(connfp);

  assert(fread(&rsp_buffer, sizeof(rsp_buffer), 1, connfp) == 1);
  bp_history = (void *) rsp_buffer.bp_history_index;
  assert(errno == 0);
}


bool
ExternalBP::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
  errno = 0;
  msg_buffer.method_id = METH_LOOKUP;
  msg_buffer.tid = tid;
  msg_buffer.branch_addr = branch_addr;
  msg_buffer.bp_history_index = (uint64_t) bp_history;

  fwrite(&msg_buffer, sizeof(msg_buffer), 1, connfp);
  fflush(connfp);

  assert(fread(&rsp_buffer, sizeof(rsp_buffer), 1, connfp) == 1);
  bp_history = (void *) rsp_buffer.bp_history_index;
  bool pred = rsp_buffer.pred;

  assert(errno == 0);
  return pred;
}


void
ExternalBP::update(ThreadID tid, Addr branch_addr, bool taken,
                   void *bp_history, bool squashed)
{
  msg_buffer.method_id = METH_UPDATE;
  msg_buffer.tid = tid;
  msg_buffer.branch_addr = branch_addr;
  msg_buffer.bp_history_index = (uint64_t) bp_history;
  msg_buffer.taken = taken;
  msg_buffer.squashed = squashed;

  fwrite(&msg_buffer, sizeof(msg_buffer), 1, connfp);
  fflush(connfp);
}


void
ExternalBP::uncondBranch(ThreadID tid, Addr pc, void *&bp_history)
{
  errno = 0;
  msg_buffer.method_id = METH_UNCOND_BRANCH;
  msg_buffer.tid = tid;
  msg_buffer.branch_addr = pc;
  msg_buffer.bp_history_index = (uint64_t) bp_history;

  fwrite(&msg_buffer, sizeof(msg_buffer), 1, connfp);
  fflush(connfp);

  assert(fread(&rsp_buffer, sizeof(rsp_buffer), 1, connfp) == 1);
  bp_history = (void *) rsp_buffer.bp_history_index;
  assert(errno == 0);
}

void
ExternalBP::squash(ThreadID tid, void * bp_history)
{
  msg_buffer.method_id = METH_SQUASH;
  msg_buffer.tid = tid;
  msg_buffer.bp_history_index = (uint64_t) bp_history;

  fwrite(&msg_buffer, sizeof(msg_buffer), 1, connfp);
  fflush(connfp);
}


ExternalBP*
ExternalBPParams::create()
{
    return new ExternalBP(this);
}
