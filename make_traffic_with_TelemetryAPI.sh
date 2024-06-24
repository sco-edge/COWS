$ wrk -t12 -c400 -d30s http://192.168.49.2:32707/productpage
Running 30s test @ http://192.168.49.2:32707/productpage
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   283.28ms  428.44ms   1.98s    89.09%
    Req/Sec    10.66      9.34    70.00     71.26%
  2046 requests in 30.09s, 10.04MB read
  Socket errors: connect 0, read 0, write 0, timeout 1771
Requests/sec:     68.00
Transfer/sec:    341.55KB
