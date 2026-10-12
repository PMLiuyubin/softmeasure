import axios from "axios";
import type { FoundationBody, SeriesRow } from "../types/api";

export const http = axios.create({ baseURL: "" });

export async function fetchFoundation() {
  const res = await http.get<FoundationBody>("/api/foundation");
  return res.data;
}

export async function fetchSeries() {
  const res = await http.get<{ grain_min: number; n: number; rows: SeriesRow[] }>("/api/series", {
    params: { grain: 15 },
  });
  return res.data;
}

export async function fetchSources() {
  const res = await http.get("/api/kb/sources", { params: { limit: 80 } });
  return res.data;
}
