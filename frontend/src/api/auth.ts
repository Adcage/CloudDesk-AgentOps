// @ts-ignore
/* eslint-disable */
import request from "@/request";

/** 此处后端没有提供注释 POST /auth/login */
export async function postAuthLogin(
  body: API.LoginRequest,
  options?: { [key: string]: any }
) {
  return request<API.Error>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    data: body,
    ...(options || {}),
  });
}

/** 此处后端没有提供注释 POST /auth/register */
export async function postAuthRegister(
  body: API.RegisterRequest,
  options?: { [key: string]: any }
) {
  return request<API.Error>("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    data: body,
    ...(options || {}),
  });
}

/** 此处后端没有提供注释 GET /users/${param0}/full */
export async function getUsersUserIdFull(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getUsersUserIdFullParams,
  options?: { [key: string]: any }
) {
  const { user_id: param0, ...queryParams } = params;
  return request<API.Error>(`/users/${param0}/full`, {
    method: "GET",
    params: { ...queryParams },
    ...(options || {}),
  });
}
