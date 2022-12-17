import { get } from "../../api";

export const load = () => get("errors");

export type PageData = Awaited<ReturnType<typeof load>>;
