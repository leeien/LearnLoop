export interface HealthResponse {
  status: string;
  service: string;
  database: string;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export async function fetchHealth(
  signal?: AbortSignal,
): Promise<HealthResponse> {
  const response = await fetch("/api/health", { signal });
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  const payload = (await response.json()) as ApiResponse<HealthResponse>;
  return payload.data;
}
