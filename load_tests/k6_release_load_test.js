import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<250', 'p(99)<500'],
    http_req_failed: ['rate<0.02']
  }
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300
  });
  sleep(1);
}
