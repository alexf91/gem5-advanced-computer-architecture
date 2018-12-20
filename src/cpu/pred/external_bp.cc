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
#include <unistd.h>

#include <cstdio>

#define BUFSIZE 1024


ExternalBP::ExternalBP(const ExternalBPParams *params)
    : BPredUnit(params)
{
  struct addrinfo *result;
  getaddrinfo("127.0.0.1", "7288", NULL, &result);

  int connfd = socket(AF_INET, SOCK_STREAM, 0);
  connect(connfd, result->ai_addr, result->ai_addrlen);
  connfp = fdopen(connfd, "r+");
  freeaddrinfo(result);
}


void
ExternalBP::btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history)
{
  fprintf(connfp, "{'method': 'btbUpdate', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'bp_history': %lu}\n",
                   tid, branch_addr, (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));
  errno = 0;
  bp_history = (void *) strtoul(line, NULL, 10);
  assert(errno == 0);
}


bool
ExternalBP::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
  fprintf(connfp, "{'method': 'lookup', "
                   "'tid': %d, "
                   "'branch_addr': %lu, "
                   "'bp_history': %lu}\n",
                   tid, branch_addr, (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));

  char *str_pred = strtok(line, ",");
  assert(str_pred);
  char *str_hist = strtok(NULL, ",");
  assert(str_hist);

  errno = 0;
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
                   "'bp_history': %lu, "
                   "'squashed': %d}\n", tid, branch_addr, taken, (uint64_t)
                                           bp_history, squashed);
  fflush(connfp);
}


void
ExternalBP::uncondBranch(ThreadID tid, Addr pc, void *&bp_history)
{
  fprintf(connfp, "{'method': 'uncondBranch', "
                   "'tid': %d, "
                   "'pc': %lu, "
                   "'bp_history': %lu}\n", tid, pc, (uint64_t) bp_history);
  fflush(connfp);

  char line[BUFSIZE];
  assert(fgets(line, BUFSIZE, connfp));

  errno = 0;
  bp_history = (void *) strtoul(line, NULL, 10);
  assert(errno == 0);
}

void
ExternalBP::squash(ThreadID tid, void * bp_history)
{
  fprintf(connfp, "{'method': 'squash', "
                   "'tid': %d, "
                   "'bp_history': %lu}\n", tid, (uint64_t) bp_history);
  fflush(connfp);
}


ExternalBP*
ExternalBPParams::create()
{
    return new ExternalBP(this);
}
