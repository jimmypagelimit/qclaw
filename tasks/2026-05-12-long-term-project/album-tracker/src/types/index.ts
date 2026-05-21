/**
 * 专辑数据库类型定义
 */

// 专辑表（对应 albums, albums_2024, albums_2025, albums_2026 表）
export interface Album {
  album_id: number;
  album_name: string;
  artist: string;
  country: string | null;
  region: string | null;
  genre: string | null;
  rating: number | null;
  description: string | null;
  is_compilation: number;
  first_listen_date: string | null;
  total_listen_count: number;
  release_company: string | null;
  cover_image_url: string | null;
  duration: string | null;
  composition_score: number | null;
  lyrics_meaning_score: number | null;
  creativity_score: number | null;
  arrangement_score: number | null;
  vocal_performance_score: number | null;
  instrumental_performance_score: number | null;
  sincerity_score: number | null;
  subjective_score: number | null;
  overall_score: number | null;
  release_year: string | null;
  style: string | null;
  producer: string | null;
}

// 创建专辑时的输入类型（部分字段可选）
export type CreateAlbumInput = Omit<Album, 'album_id'> & {
  album_name: string;
  artist: string;
};

// 更新专辑时的输入类型
export type UpdateAlbumInput = Partial<Omit<Album, 'album_id'>>;

// 查询专辑的参数
export interface QueryAlbumsParams {
  keyword?: string;
  artist?: string;
  genre?: string;
  year?: string;
  country?: string;
  limit?: number;
  offset?: number;
}

// 统计信息
export interface AlbumStats {
  totalCount: number;
  totalListenCount: number;
  avgListenCount: number;
  maxListenCount: number;
  maxListenAlbum?: Album;
}

// 风格分布统计
export interface GenreStats {
  genre: string;
  count: number;
  percentage: number;
}

// 国家分布统计
export interface CountryStats {
  country: string;
  count: number;
  percentage: number;
}

// 年份分布统计
export interface YearStats {
  year: string;
  count: number;
}

// 数据库配置
export interface DatabaseConfig {
  path: string;
}

// CLI 命令选项
export interface BaseCommandOptions {
  table?: string;
  output?: string;
}
