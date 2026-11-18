"""Claim check: each (key, phrase) must appear in the cached text of that source.

Usage: python3 claims.py            (all)
       python3 claims.py key ...    (only these keys)
A phrase that is a regex starts with "re:".
"""
import os
import re
import sys

from check_sources import norm

HERE = os.path.dirname(os.path.abspath(__file__))

CLAIMS = [
    # m4 communication
    ("fielding", "uniform interface"),
    ("fielding", "resource identifier"),
    ("rfc9110", "re:put ?, delete ?, and safe request methods are idempotent"),
    ("graphql-spec", "selection set"),
    ("graphql-security", "depth"),
    ("graphql-security", "complexity"),
    ("grpc-intro", "re:generat"),
    ("slack-pagination", "re:skip|duplicat|miss"),
    ("stripe-versioning", "re:pin|first api request|locked"),
    ("rabbit-confirms", "re:redeliver"),
    ("sqs-visibility", "re:visible again|becomes visible|available for other consumers"),
    ("kafka-intro", "same partition"),
    ("kafka-intro", "re:zero, one, or many consumers"),
    ("kafka-intro", "re:read as often as needed"),
    ("kafka-intro", "re:how long kafka should retain your events"),
    ("confluent-consumer", "re:read from a topic's partitions in parallel"),
    ("confluent-consumer", "re:tracks each consumer's position"),
    ("confluent-consumer", "re:extra consumers can sit idle"),
    ("gcp-pubsub", "re:delivers events to all the services that react to them"),
    ("fowler-events", "re:not explicit in any program text"),
    ("html-sse", "re:push data to web pages over http"),
    ("html-sse", "re:reconnect"),
    ("rfc6455", "upgrade"),
    # m5 reliability
    ("sre-risk", "re:100% is probably never the right reliability target"),
    ("aws-az", "re:generators and cooling equipment"),
    ("aws-az", "re:different power substations"),
    ("chaos-monkey", "re:inside of your production environment"),
    ("sre-canary", "re:roll ?back"),
    ("stripe-limiters", "re:critical"),
    ("cf-counting", "re:information from the previous counter"),
    ("sre-overload", "per-customer"),
    ("sre-overload", "client-side throttling"),
    ("aws-timeouts", "re:p99\\.9|99\\.9"),
    ("aws-timeouts", "re:retries at each layer mul"),
    ("aws-jitter", "re:substantial decrease in client work and server load"),
    ("sre-monitoring", "re:how \"full\" your service is|how full"),
    ("sre-slo-alerts", "re:how fast"),
    ("otel-traces", "re:trace id|trace_id"),
    ("otel-traces", "re:start time|start_time"),
    # m6 architecture
    ("fowler-monolith-first", "re:boundar"),
    ("fowler-microservices", "re:independently deployable"),
    ("db-per-service", "re:only via its api|accessible only via"),
    ("cqrs", "re:event"),
    ("cdc-contracts", "re:provider"),
    ("ms-client-disc", "re:obtains the location of a service instance by querying a service registry"),
    ("ms-server-disc", "re:forward"),
    ("k8s-dns", "svc.cluster.local"),
    ("k8s-probes", "re:ready to accept traffic"),
    ("k8s-probes", "re:stop sending traffic to containers that are not ready"),
    ("envoy-slow-start", "re:progressively increase amount of traffic"),
    ("istio", "re:mutual tls encryption"),
    ("istio", "re:load balancing, service-to-service authentication, and monitoring - with few or no service code changes"),
    ("ms-gateway", "re:backends for frontends"),
    ("gray-lamport", "re:two-phase commit protocol blocks if the coordinator fails"),
    ("sagas-paper", "re:compensat"),
    ("sagas-paper", "re:reverse order"),
    ("mapreduce", "re:partial merging"),
    ("hll", "re:2%|2 %"),
    ("hll", "1.5 kilobytes"),
    ("hll", "re:well beyond 10 ?9"),
    ("flink-time", "re:event time has reached time t"),
    ("kreps-lambda", "re:reprocess"),
    # m7 security
    ("owasp-passwords", "re:19 mib"),
    ("owasp-passwords", "re:iteration count of 2"),
    ("owasp-passwords", "re:work factor of 10"),
    ("owasp-sessions", "re:renew|regenerat"),
    ("owasp-sessions", "re:idle timeout"),
    ("owasp-forgot", "re:consistent message for both existent and non-existent accounts"),
    ("owasp-stuffing", "re:by far the best defen[cs]e"),
    ("webauthn", "re:public key"),
    ("webauthn", "re:challenge signed by the private key"),
    ("webauthn", "re:signature changes with the origin of the website"),
    ("fido-passkeys", "re:phishing[ -]resistant"),
    ("owasp-bola", "re:api1:2023"),
    ("zanzibar", "re:calendar, cloud, drive, maps, photos, and youtube"),
    ("opa", "re:decouple"),
    ("owasp-logging", "re:tamper"),
    ("nist-zero-trust", "re:implicit trust"),
    ("aws-kms-rotate", "re:decrypt"),
    ("vault-dynamic", "re:within a reasonable time of the lease expiring"),
    ("rfc9700", "re:access tokens with a short lifetime"),
    ("pci-token", "re:scope"),
    ("k8s-components", "re:consistent and highly-available key value store"),
    # m8 shipping
    ("fowler-mocks", "re:fake objects actually have working implementations"),
    ("fowler-mocks", "re:in memory database is a good example"),
    ("fowler-mocks", "re:stubs provide canned answers"),
    ("fowler-mocks", "re:spies are stubs that also record"),
    ("fowler-mocks", "re:objects pre-programmed with expectations"),
    ("fowler-mocks", "re:dummy objects are passed around but never actually used"),
    ("practical-pyramid", "re:integration of your application with all the parts that live outside"),
    ("practical-pyramid", "re:consumers of an interface write tests that check the interface for all data they need"),
    ("practical-pyramid", "re:pact : for writing cdc tests"),
    ("practical-pyramid", "re:notoriously flaky"),
    ("cdc-contracts", "re:enforced in a repeatable, automated fashion with each build"),
    ("fowler-pyramid", "re:many more low-level unit ?tests than high level broad-?stack ?tests running through a gui"),
    ("google-flaky", "re:1\\.5% of test results are flaky"),
    ("google-flaky", "re:almost 16% of our tests have some level of flakiness"),
    ("google-flaky", "re:automatically quarantines the test"),
    ("google-flaky", "re:files a bug"),
    ("chaos-principles", "re:discipline of experimenting on a system in order to build confidence"),
    ("fowler-ci", "re:everyone pushes commits to the mainline every day"),
    ("fowler-ci", "re:every push to mainline should trigger a build"),
    ("fowler-ci", "re:fix broken builds immediately"),
    ("fowler-ci", "re:make the build self-testing"),
    ("fowler-ci", "re:ten minute build is perfectly within reason"),
    ("fowler-pipeline", "re:breaking up your build into stages"),
    ("fowler-pipeline", "re:first stage of a deployment pipeline will do any compilation and provide binaries"),
    ("fowler-cd", "re:can be released to production at any time"),
    ("fowler-cd", "re:every change goes through the pipeline and automatically gets put into production"),
    ("fowler-bluegreen", "re:two production environments, as identical as possible"),
    ("fowler-bluegreen", "re:switch the router back to your blue environment"),
    ("fowler-canary", "re:small subset of users before rolling it out to the entire infrastructure"),
    ("fowler-canary", "re:reroute users back to the old version"),
    ("fowler-parallel", "re:three distinct phases: expand, migrate, and contract"),
    ("feature-toggles", "re:separating \\[feature\\] release from \\[code\\] deployment"),
    ("feature-toggles", "re:not stick around much longer than a week or two"),
    ("dora", "re:three factors to measure software delivery throughput"),
    ("dora", "re:deployment rework rate"),
    ("dora", "re:speed and stability are not tradeoffs"),
    ("dora", "re:top performers do well across all"),
    # m9 whole systems
    ("c4", "re:system context , containers , components , and code"),
    ("design-docs", "re:emphasis on the trade-offs that were considered"),
    ("rfc9110", "re:has been assigned a new permanent uri"),
    ("rfc9110", "re:a 301 response is heuristically cacheable"),
    ("rfc9110", "re:resides temporarily under a different uri"),
    ("rfc9110", "re:ought to continue to use the target uri for future requests"),
    ("safe-browsing", "re:check urls against google's constantly updated lists of unsafe web resources"),
    ("safe-browsing", "re:social engineering sites \\(phishing"),
    ("safe-browsing", "re:malware"),
    ("feeding-frenzy", "re:high-rate producers are retrieved at query time"),
    ("feeding-frenzy", "re:lower-rate producers are materialized"),
    ("fb-tao", "re:a billion reads and millions of writes each second"),
    ("slack-rtm", "re:gateway servers \\(gs\\) are stateful and in-memory"),
    ("slack-rtm", "re:websocket channel subscriptions"),
    ("slack-rtm", "re:interface between slack clients and css"),
    ("slack-rtm", "re:keep track of which users are online"),
    ("discord-messages", "re:the primary key became \\(channel_id, message_id\\)"),
    ("discord-messages", "re:chronologically sortable"),
    ("discord-messages", "re:channel_id became the partition key"),
    ("fb-messenger", "re:totally ordered queue of messaging updates"),
    ("fb-messenger", "re:pointer stays in place"),
]


def text_of(key: str) -> str:
    path = os.path.join(HERE, "cache", key + ".txt")
    return norm(open(path, encoding="utf-8").read()) if os.path.exists(path) else ""


def main():
    want = set(sys.argv[1:])
    bad = 0
    for key, phrase in CLAIMS:
        if want and key not in want:
            continue
        t = text_of(key)
        if phrase.startswith("re:"):
            ok = re.search(phrase[3:], t) is not None
        else:
            ok = norm(phrase) in t
        if not ok:
            bad += 1
            print(f"MISS {key}: {phrase}  (cache {len(t)} chars)")
    n = sum(1 for k, _ in CLAIMS if not want or k in want)
    print(f"{n - bad}/{n} claims found")


if __name__ == "__main__":
    main()
