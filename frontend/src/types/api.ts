export interface ApiResponse<T> {
  data: T;
  message: string;
  status_code: number;
}

export interface PaginatedApiResponse<T> extends ApiResponse<T[]> {
  page: number;
  page_size: number;
  total_data: number;
  total_page: number;
  filter_options: {
    node_locations: string[];
    node_types: string[];
  };
}

export interface ApiError {
  message: string;
  status_code: number;
}
