import { Container, getContainer } from '@cloudflare/containers';

export class WordBreakdownContainer extends Container {
  defaultPort = 8000;
  sleepAfter = '5m';
  enableInternet = false;
}

interface Env {
  WORD_BREAKDOWN: DurableObjectNamespace<WordBreakdownContainer>;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return getContainer(env.WORD_BREAKDOWN).fetch(request);
  },
};
