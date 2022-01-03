# travel-app
Problem:
Prepare a small application  where you use the MBTA API (https://www.mbta.com/developers/v3-api)
which is a set of proprietary messages exchanged over http/REST API or http Server Send Events protocol
to build a website that shows a commuter rail departure board that displays in real time
commuter rail carrier,destination, departure time,train number,track number,status.
The project should be done utilizing Python.

Proposed Solution:(which I did implement)
The Observer pattern was used to define publishers that run background "Greenlets"
that are able to monitor in real time commuter rail ,subway,bus and various traffic status and to define
subscribers that are "Greenlets" interested in displaying specific "subjects". The "Greenlets"  in gevents libraries or
asynchio.coroutines decorators are defined as linked coroutines/generators which defer the waiting for multiple network I/O events  
to a single place in the code (the "event loop"). how to resume the one piece of code expecting to receive that network I/O event
can be achieved by calculating where coroutines got suspended. Why propose doing this? for example,if a single synchronous  network I/O  operation such as urlopen() takes X seconds and if we call urlopen() N times sequentially then latency would be N*X seconds.
but if we call gevent.spawn(urlopen) N times sequestially,the latency will be X seconds total for all N calls to urlopen--so N*X seconds latency reduced to X seconds hopefully.
given its Python and its clear we need concurrency and given many asynchronous network I/O tasks and each task is small and independent of each other,then the above Greenlet strategy might have higher throughput compared with multithreading/parallelism. also the above
Greenlet strategy avoids overhead of context switching and system scheduler compared with multithreading.
The Greenlet strategy uses less memory (does not use stack space) and avoids latency of copying large argument data to stack space as in C++/JAVA multithreading.
Finally, the Greenlets can never be suspended at arbitrary times so in theory you can get away
with fewer locks and mutexes because greenlet execution  context switching is deterministic so in theory you can calculate when different greenlets will suspend and resume and avoid locks which might increase throughput. (I did not yet do this  so it is a potential area for
improvement if speed is required).Note that multiple Greenlets all execute in single thread due to the GIL so for scalability we could increase the number of processes (each process has one thread running multiple greenlets)

The UI was simply an EventSource js object which communicates with Server Sent Events protocol( a node.js concept)
which should run on most browsers except for IE. if IE support is important then I would probably implement 
web sockets protocol using geventwebsocket.handler using same gevents.pywsgi (which I did not yet implement)

 









