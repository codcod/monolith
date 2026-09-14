import http from "k6/http";
import { check } from "k6";

// traffic has no public HTTP surface beyond /health (its real work is
// consuming traffic-in and publishing to dispatch-in over RabbitMQ
// Streams, which k6 doesn't drive) — this is a liveness/latency check
// on /health, not a throughput test of the service's actual job.
//
// Run against a live instance: docker compose up (or `just traffic::run`),
// then from platform/traffic:
//   BASE_URL=http://localhost:8080 k6 run tests/performance/k6/script.js

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";

export const options = {
  vus: 5,
  duration: "15s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<100"],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, { "status is 200": (r) => r.status === 200 });
}
