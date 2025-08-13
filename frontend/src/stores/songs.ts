import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { songsService } from '@/services/songs'
import type {
  Song,
  SongContent,
  CreateSongData,
  UpdateSongData,
  UpdateSongContentData,
  SearchParams,
  SongSearchFilters,
  PaginatedResponse,
} from '@/types'

export const useSongsStore = defineStore('songs', () => {
  // State
  const songs = ref<Song[]>([])
  const currentSong = ref<Song | null>(null)
  const currentSongContent = ref<SongContent | null>(null)
  const searchResults = ref<Song[]>([])
  const searchQuery = ref('')
  const searchFilters = ref<SongSearchFilters>({})
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  })
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasMore = computed(() => pagination.value.page < pagination.value.pages)
  const filteredSongs = computed(() => {
    if (!searchQuery.value && Object.keys(searchFilters.value).length === 0) {
      return songs.value
    }
    return searchResults.value
  })

  // Actions
  const fetchSongs = async (params: SearchParams & { filters?: SongSearchFilters } = {}) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await songsService.getSongs({
        page: pagination.value.page,
        size: pagination.value.size,
        ...params,
      })

      if (params.page === 1 || !params.page) {
        songs.value = response.items
      } else {
        songs.value.push(...response.items)
      }

      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || '獲取歌曲列表失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const searchSongs = async (query: string, filters: SongSearchFilters = {}) => {
    try {
      isLoading.value = true
      error.value = null
      searchQuery.value = query
      searchFilters.value = filters

      const response = await songsService.getSongs({
        query,
        filters,
        page: 1,
        size: pagination.value.size,
      })

      searchResults.value = response.items
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || '搜索歌曲失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadMoreSongs = async () => {
    if (!hasMore.value || isLoading.value) return

    const nextPage = pagination.value.page + 1

    if (searchQuery.value || Object.keys(searchFilters.value).length > 0) {
      await searchSongs(searchQuery.value, searchFilters.value)
    } else {
      await fetchSongs({ page: nextPage })
    }
  }

  const getSong = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null

      const song = await songsService.getSong(id)
      currentSong.value = song

      // 增加瀏覽次數
      songsService.incrementViewCount(id).catch(console.warn)

      return song
    } catch (err: any) {
      error.value = err.message || '獲取歌曲詳情失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getSongContent = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null

      const content = await songsService.getSongContent(id)
      currentSongContent.value = content

      return content
    } catch (err: any) {
      error.value = err.message || '獲取歌曲內容失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createSong = async (data: CreateSongData) => {
    try {
      isLoading.value = true
      error.value = null

      const song = await songsService.createSong(data)

      // 添加到列表開頭
      songs.value.unshift(song)
      currentSong.value = song

      return song
    } catch (err: any) {
      error.value = err.message || '創建歌曲失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateSong = async (id: string, data: Partial<UpdateSongData>) => {
    try {
      isLoading.value = true
      error.value = null

      const updatedSong = await songsService.updateSong(id, data)

      // 更新列表中的歌曲
      const index = songs.value.findIndex((song) => song.id === id)
      if (index !== -1) {
        songs.value[index] = updatedSong
      }

      // 更新當前歌曲
      if (currentSong.value?.id === id) {
        currentSong.value = updatedSong
      }

      return updatedSong
    } catch (err: any) {
      error.value = err.message || '更新歌曲失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateSongContent = async (id: string, data: UpdateSongContentData) => {
    try {
      isLoading.value = true
      error.value = null

      const updatedContent = await songsService.updateSongContent(id, data)
      currentSongContent.value = updatedContent

      return updatedContent
    } catch (err: any) {
      error.value = err.message || '更新歌曲內容失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteSong = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null

      await songsService.deleteSong(id)

      // 從列表中移除
      songs.value = songs.value.filter((song) => song.id !== id)
      searchResults.value = searchResults.value.filter((song) => song.id !== id)

      // 清除當前歌曲
      if (currentSong.value?.id === id) {
        currentSong.value = null
        currentSongContent.value = null
      }
    } catch (err: any) {
      error.value = err.message || '刪除歌曲失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const duplicateSong = async (id: string, title?: string) => {
    try {
      isLoading.value = true
      error.value = null

      const duplicatedSong = await songsService.duplicateSong(id, title)

      // 添加到列表開頭
      songs.value.unshift(duplicatedSong)

      return duplicatedSong
    } catch (err: any) {
      error.value = err.message || '複製歌曲失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const rateSong = async (id: string, score: number, comment?: string) => {
    try {
      error.value = null

      const rating = await songsService.rateSong(id, { score, comment })

      // 更新歌曲評分
      const song = songs.value.find((s) => s.id === id)
      if (song) {
        // 重新計算平均評分（簡化處理）
        const totalScore = song.average_rating * song.rating_count + score
        song.rating_count += 1
        song.average_rating = totalScore / song.rating_count
      }

      if (currentSong.value?.id === id) {
        const totalScore = currentSong.value.average_rating * currentSong.value.rating_count + score
        currentSong.value.rating_count += 1
        currentSong.value.average_rating = totalScore / currentSong.value.rating_count
      }

      return rating
    } catch (err: any) {
      error.value = err.message || '評分失敗'
      throw err
    }
  }

  const clearCurrentSong = () => {
    currentSong.value = null
    currentSongContent.value = null
  }

  const clearSearch = () => {
    searchQuery.value = ''
    searchFilters.value = {}
    searchResults.value = []
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    songs,
    currentSong,
    currentSongContent,
    searchResults,
    searchQuery,
    searchFilters,
    pagination,
    isLoading,
    error,

    // Getters
    hasMore,
    filteredSongs,

    // Actions
    fetchSongs,
    searchSongs,
    loadMoreSongs,
    getSong,
    getSongContent,
    createSong,
    updateSong,
    updateSongContent,
    deleteSong,
    duplicateSong,
    rateSong,
    clearCurrentSong,
    clearSearch,
    clearError,
  }
})
