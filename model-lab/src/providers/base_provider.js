/** Base provider interface. */
class BaseProvider {
  constructor(config = {}) {
    this.config = config;
  }

  async generate(_opts) {
    throw new Error("generate() not implemented");
  }

  async healthCheck() {
    return { ok: false, message: "not implemented" };
  }
}

module.exports = { BaseProvider };
