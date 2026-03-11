#!/usr/bin/env bash
# kill any uvicorn process
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs -r kill -9
