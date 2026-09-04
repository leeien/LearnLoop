export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  cache_hit?: boolean | null;
}
