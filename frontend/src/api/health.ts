// @ts-ignore
/* eslint-disable */
import request from "@/request";

/** 此处后端没有提供注释 GET /health */
export async function getHealth(options?: { [key: string]: any }) {
  return request<API.Error>("/health", {
    method: "GET",
    ...(options || {}),
  });
}
