import http from "k6/http";
import { check } from "k6";

// Minimal load smoke test for inbox's only real endpoint.
// Run against a live instance: docker compose up (or `just inbox::run`),
// then from platform/inbox:
//   BASE_URL=http://localhost:8080 AUTH_TOKEN=dev-token k6 run tests/performance/k6/script.js

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const AUTH_TOKEN = __ENV.AUTH_TOKEN || "dev-token";

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<200"],
  },
};

const CHANNELS = ["sms", "email", "whatsapp"];

export default function () {
  const channel = CHANNELS[Math.floor(Math.random() * CHANNELS.length)];

  const res = http.post(
    `${BASE_URL}/messages`,
    JSON.stringify({
      channel,
      recipient: "+15550000000",
      body: "load test message",
    }),
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${AUTH_TOKEN}`,
      },
    }
  );

  check(res, {
    "status is 202": (r) => r.status === 202,
    "returns an id": (r) => JSON.parse(r.body).id !== undefined,
  });
}
