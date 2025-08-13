import { ApiService } from './api'
import type {
  Song,
  SongContent,
  CreateSongData,
  UpdateSongData,
  UpdateSongContentData,
  SearchParams,
  PaginatedResponse,
  SongSearchFilters,
  Rating,
  CreateRatingData,
} from '@/types'

export class SongsService extends ApiService {
  /**
   * 獲取歌曲列表（分頁、搜索、篩選）
   */
  async getSongs(
    params: SearchParams & { filters?: SongSearchFilters } = {},
  ): Promise<PaginatedResponse<Song>> {
    const queryParams = new URLSearchParams()

    // 基本參數
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.size) queryParams.append('size', params.size.toString())
    if (params.sort) queryParams.append('sort', params.sort)
    if (params.order) queryParams.append('order', params.order)
    if (params.query) queryParams.append('query', params.query)

    // 篩選參數
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString())
        }
      })
    }

    return this.get<PaginatedResponse<Song>>(`/songs?${queryParams.toString()}`)
  }

  /**
   * 獲取單個歌曲詳情
   */
  async getSong(id: string): Promise<Song> {
    return this.get<Song>(`/songs/${id}`)
  }

  /**
   * 獲取歌曲內容
   */
  async getSongContent(id: string): Promise<SongContent> {
    return this.get<SongContent>(`/songs/${id}/content`)
  }

  /**
   * 創建新歌曲
   */
  async createSong(data: CreateSongData): Promise<Song> {
    return this.post<Song>('/songs', data)
  }

  /**
   * 更新歌曲資訊
   */
  async updateSong(id: string, data: Partial<UpdateSongData>): Promise<Song> {
    return this.put<Song>(`/songs/${id}`, data)
  }

  /**
   * 更新歌曲內容
   */
  async updateSongContent(id: string, data: UpdateSongContentData): Promise<SongContent> {
    return this.put<SongContent>(`/songs/${id}/content`, data)
  }

  /**
   * 刪除歌曲
   */
  async deleteSong(id: string): Promise<void> {
    return this.delete<void>(`/songs/${id}`)
  }

  /**
   * 複製歌曲
   */
  async duplicateSong(id: string, title?: string): Promise<Song> {
    return this.post<Song>(`/songs/${id}/duplicate`, { title })
  }

  /**
   * 獲取歌曲評分
   */
  async getSongRatings(id: string, params: SearchParams = {}): Promise<PaginatedResponse<Rating>> {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.size) queryParams.append('size', params.size.toString())

    return this.get<PaginatedResponse<Rating>>(`/songs/${id}/ratings?${queryParams.toString()}`)
  }

  /**
   * 為歌曲評分
   */
  async rateSong(id: string, data: CreateRatingData): Promise<Rating> {
    return this.post<Rating>(`/songs/${id}/rate`, data)
  }

  /**
   * 更新評分
   */
  async updateRating(
    songId: string,
    ratingId: string,
    data: Partial<CreateRatingData>,
  ): Promise<Rating> {
    return this.put<Rating>(`/songs/${songId}/ratings/${ratingId}`, data)
  }

  /**
   * 刪除評分
   */
  async deleteRating(songId: string, ratingId: string): Promise<void> {
    return this.delete<void>(`/songs/${songId}/ratings/${ratingId}`)
  }

  /**
   * 獲取熱門歌曲
   */
  async getPopularSongs(limit: number = 10): Promise<Song[]> {
    return this.get<Song[]>(`/songs/popular?limit=${limit}`)
  }

  /**
   * 獲取最新歌曲
   */
  async getLatestSongs(limit: number = 10): Promise<Song[]> {
    return this.get<Song[]>(`/songs/latest?limit=${limit}`)
  }

  /**
   * 獲取推薦歌曲
   */
  async getRecommendedSongs(limit: number = 10): Promise<Song[]> {
    return this.get<Song[]>(`/songs/recommended?limit=${limit}`)
  }

  /**
   * 搜索建議
   */
  async getSearchSuggestions(query: string, limit: number = 5): Promise<string[]> {
    return this.get<string[]>(
      `/songs/search-suggestions?query=${encodeURIComponent(query)}&limit=${limit}`,
    )
  }

  /**
   * 增加歌曲瀏覽次數
   */
  async incrementViewCount(id: string): Promise<void> {
    return this.post<void>(`/songs/${id}/view`)
  }

  /**
   * 匯出歌曲
   */
  async exportSong(id: string, format: 'pdf' | 'txt' | 'json' = 'pdf'): Promise<Blob> {
    const response = await this.client.get(`/songs/${id}/export?format=${format}`, {
      responseType: 'blob',
    })
    return response.data
  }

  /**
   * 獲取我的歌曲
   */
  async getMySongs(params: SearchParams = {}): Promise<PaginatedResponse<Song>> {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.size) queryParams.append('size', params.size.toString())
    if (params.sort) queryParams.append('sort', params.sort)
    if (params.order) queryParams.append('order', params.order)
    if (params.query) queryParams.append('query', params.query)

    return this.get<PaginatedResponse<Song>>(`/songs/my?${queryParams.toString()}`)
  }
}

// 創建單例實例
export const songsService = new SongsService()
