// 音樂理論相關類型定義

// 基本音樂元素
export type Note =
  | 'C'
  | 'C#'
  | 'Db'
  | 'D'
  | 'D#'
  | 'Eb'
  | 'E'
  | 'F'
  | 'F#'
  | 'Gb'
  | 'G'
  | 'G#'
  | 'Ab'
  | 'A'
  | 'A#'
  | 'Bb'
  | 'B'

export type ChordQuality =
  | 'maj'
  | 'min'
  | 'dim'
  | 'aug'
  | 'sus2'
  | 'sus4'
  | '7'
  | 'maj7'
  | 'min7'
  | 'dim7'
  | 'aug7'
  | '9'
  | '11'
  | '13'

export type Difficulty = 'beginner' | 'intermediate' | 'advanced' | 'expert'

export type Genre = 'pop' | 'rock' | 'folk' | 'country' | 'jazz' | 'blues' | 'classical' | 'other'

// 和絃相關類型
export interface ChordInfo {
  symbol: string
  root: Note
  quality: ChordQuality
  extension?: string
  bass?: Note
}

export interface ChordDefinition {
  id: string
  symbol: string
  root_note: Note
  chord_type: ChordQuality
  fingering_patterns: FingeringPattern[]
  note_composition: NoteComposition
  alternative_names: string[]
  difficulty_level: number
}

export interface FingeringPattern {
  id: string
  name: string
  frets: number[] // [0, 0, 2, 2, 2, 0] 代表各弦品位
  fingers: number[] // [0, 0, 1, 2, 3, 0] 代表手指編號
  difficulty: number
  is_default: boolean
}

export interface NoteComposition {
  root: Note
  third?: Note
  fifth?: Note
  seventh?: Note
  ninth?: Note
  eleventh?: Note
  thirteenth?: Note
}

// 歌曲相關類型
export interface Song {
  id: string
  author_id: string
  title: string
  artist: string
  key_signature: Note
  capo_position: number
  bpm: number
  difficulty: Difficulty
  genre: Genre
  description?: string
  average_rating: number
  rating_count: number
  view_count: number
  is_public: boolean
  created_at: string
  updated_at: string
  author?: {
    id: string
    display_name: string
  }
}

export interface SongContent {
  id: string
  song_id: string
  lyrics: string
  chord_positions: ChordPosition[]
  structure_metadata: SongStructure
  version_created_at: string
}

export interface ChordPosition {
  line: number
  position: number
  chord: string
  duration?: number
}

export interface SongStructure {
  intro?: { start: number; end: number }
  verse1?: { start: number; end: number }
  chorus?: { start: number; end: number }
  verse2?: { start: number; end: number }
  bridge?: { start: number; end: number }
  outro?: { start: number; end: number }
  playback_settings?: PlaybackSettings
}

export interface PlaybackSettings {
  default_bpm: number
  scroll_speed: number
  auto_scroll_enabled: boolean
}

// 創建和更新歌曲的數據類型
export interface CreateSongData {
  title: string
  artist: string
  key_signature: Note
  capo_position?: number
  bpm?: number
  difficulty?: Difficulty
  genre?: Genre
  description?: string
  is_public?: boolean
}

export interface UpdateSongData extends Partial<CreateSongData> {
  id: string
}

export interface UpdateSongContentData {
  lyrics: string
  chord_positions: ChordPosition[]
  structure_metadata?: SongStructure
}

// 評分相關類型
export interface Rating {
  id: string
  user_id: string
  song_id: string
  score: number // 1-5 星評分
  comment?: string
  created_at: string
}

export interface CreateRatingData {
  score: number
  comment?: string
}

// 搜索和篩選類型
export interface SongSearchFilters {
  key_signature?: Note
  difficulty?: Difficulty
  genre?: Genre
  capo_position?: number
  bpm_min?: number
  bpm_max?: number
  rating_min?: number
}

// 音樂理論計算相關
export interface TransposeRequest {
  chord_symbol: string
  semitones: number
}

export interface TransposeResponse {
  original_chord: string
  transposed_chord: string
  semitones: number
}

export interface CapoCalculation {
  original_key: Note
  capo_position: number
  effective_key: Note
  relative_chords: Record<string, string>
}

// 六線譜相關類型
export interface TabNotation {
  frets: number[] // [3, 2, 0, 1, 0, 0] 代表各弦的品位
  fingers: number[] // [3, 2, 0, 1, 0, 0] 代表使用的手指
  tuning: string[] // ['E', 'A', 'D', 'G', 'B', 'E'] 標準調弦
}

export interface TabRenderOptions {
  frets?: number
  showFretNumbers?: boolean
  showFingers?: boolean
  showStringNames?: boolean
  width?: number
  height?: number
}
