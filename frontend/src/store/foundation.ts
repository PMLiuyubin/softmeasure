import { defineStore } from "pinia";
import { fetchFoundation } from "../api/http";
import type { FoundationBody } from "../types/api";

export const useFoundation = defineStore("foundation", {
  state: () => ({ body: null as FoundationBody | null, error: "" }),
  actions: {
    async load() {
      try {
        this.body = await fetchFoundation();
        this.error = "";
      } catch (err) {
        this.error = err instanceof Error ? err.message : "接口不可用";
      }
    },
  },
});
