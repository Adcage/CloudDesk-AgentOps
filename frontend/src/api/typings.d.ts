declare namespace API {
  type Error = {
    /** Error code */
    code?: number;
    /** Error name */
    status?: string;
    /** Error message */
    message?: string;
    /** Errors */
    errors?: Record<string, any>;
  };

  type getUsersUserIdFullParams = {
    user_id: number;
  };

  type LoginRequest = {
    account?: string;
    password?: string;
  };

  type PaginationMetadata = {
    total?: number;
    total_pages?: number;
    first_page?: number;
    last_page?: number;
    page?: number;
    previous_page?: number;
    next_page?: number;
  };

  type RegisterRequest = {
    account?: string;
    password?: string;
  };

  type ResponseEnvelope = {
    code: string;
    message: string;
    request_id: string;
    data: any;
  };
}
