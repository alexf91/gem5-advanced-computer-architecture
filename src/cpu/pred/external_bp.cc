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
  fprintf(connfp, "{'method': 'btb_update', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'bp_history_index': %lu}\n",
                   tid, branch_addr, (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));
  bp_history = (void *) strtoul(line, NULL, 10);
  assert(errno == 0);
}


bool
ExternalBP::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
  errno = 0;
  fprintf(connfp, "{'method': 'lookup', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'bp_history_index': %lu}\n",
                   tid, branch_addr, (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));

  char *str_pred = strtok(line, ",");
  assert(str_pred);
  char *str_hist = strtok(NULL, ",");
  assert(str_hist);

  bp_history = (void *) strtoul(str_hist, NULL, 10);
  bool pred = strtol(str_pred, NULL, 10);
  assert(errno == 0);
  return pred;
}


void
ExternalBP::update(ThreadID tid, Addr branch_addr, bool taken,
                   void *bp_history, bool squashed)
{
  fprintf(connfp, "{'method': 'update', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'taken': %d, "
                   "'bp_history_index': %lu, "
                   "'squashed': %d}\n", tid, branch_addr, taken, (uint64_t)
                                           bp_history, squashed);
  fflush(connfp);
}


void
ExternalBP::uncondBranch(ThreadID tid, Addr pc, void *&bp_history)
{
  errno = 0;
  fprintf(connfp, "{'method': 'uncond_branch', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'bp_history_index': %lu}\n", tid, pc,
                                                 (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));

  bp_history = (void *) strtoul(line, NULL, 10);
  assert(errno == 0);
}

void
ExternalBP::squash(ThreadID tid, void * bp_history)
{
  fprintf(connfp, "{'method': 'squash', "
                   "'tid': %d, "
                   "'bp_history_index': %lu}\n", tid, (uint64_t) bp_history);
  fflush(connfp);
}


ExternalBP*
ExternalBPParams::create()
{
    return new ExternalBP(this);
}
