-- MyChordHub 資料庫初始化腳本
-- 創建資料庫和基本結構

-- 設置時區
SET timezone = 'UTC';

-- 創建擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 用戶表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 歌曲表
CREATE TABLE songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    key VARCHAR(10) NOT NULL,
    capo INTEGER DEFAULT 0,
    tempo INTEGER DEFAULT 80,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    lyrics_with_chords TEXT NOT NULL,
    notes TEXT,
    tags TEXT[],
    is_public BOOLEAN DEFAULT TRUE,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 自定義和絃表
CREATE TABLE custom_chords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(20) NOT NULL,
    frets INTEGER[] NOT NULL, -- 六個品位，-1表示不按
    fingers INTEGER[] NOT NULL, -- 對應的手指位置
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 收藏表
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, song_id)
);

-- 評分表
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, song_id)
);

-- 創建索引
CREATE INDEX idx_songs_title ON songs USING gin(title gin_trgm_ops);
CREATE INDEX idx_songs_artist ON songs USING gin(artist gin_trgm_ops);
CREATE INDEX idx_songs_key ON songs(key);
CREATE INDEX idx_songs_created_by ON songs(created_by);
CREATE INDEX idx_songs_is_public ON songs(is_public);
CREATE INDEX idx_songs_created_at ON songs(created_at DESC);
CREATE INDEX idx_songs_rating_avg ON songs(rating_avg DESC);

CREATE INDEX idx_custom_chords_name ON custom_chords(name);
CREATE INDEX idx_custom_chords_created_by ON custom_chords(created_by);
CREATE INDEX idx_custom_chords_is_public ON custom_chords(is_public);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_song_id ON favorites(song_id);

CREATE INDEX idx_ratings_song_id ON ratings(song_id);
CREATE INDEX idx_ratings_user_id ON ratings(user_id);

-- 創建更新時間的觸發器函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 創建觸發器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_songs_updated_at BEFORE UPDATE ON songs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON ratings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 更新歌曲評分的觸發器函數
CREATE OR REPLACE FUNCTION update_song_rating()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE songs 
        SET 
            rating_avg = (SELECT AVG(rating)::DECIMAL(3,2) FROM ratings WHERE song_id = NEW.song_id),
            rating_count = (SELECT COUNT(*) FROM ratings WHERE song_id = NEW.song_id)
        WHERE id = NEW.song_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE songs 
        SET 
            rating_avg = COALESCE((SELECT AVG(rating)::DECIMAL(3,2) FROM ratings WHERE song_id = OLD.song_id), 0.00),
            rating_count = (SELECT COUNT(*) FROM ratings WHERE song_id = OLD.song_id)
        WHERE id = OLD.song_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- 創建評分更新觸發器
CREATE TRIGGER update_song_rating_trigger
    AFTER INSERT OR UPDATE OR DELETE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_song_rating();

-- 插入一些範例數據
INSERT INTO users (id, email, username, hashed_password) VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'demo@mychordhub.com', 'demo', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiDDQ.xPYBhG'),
    ('550e8400-e29b-41d4-a716-446655440001', 'user@mychordhub.com', 'user', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiDDQ.xPYBhG');

-- 插入範例歌曲
INSERT INTO songs (id, title, artist, key, capo, tempo, created_by, lyrics_with_chords, notes) VALUES 
    ('660e8400-e29b-41d4-a716-446655440000', 'Amazing Grace', 'Traditional', 'C', 0, 80, '550e8400-e29b-41d4-a716-446655440000', 
     '[C]Amazing [F]grace how [C]sweet the sound
That [C]saved a [G]wretch like [C]me
I [C]once was [F]lost but [C]now am found
Was [C]blind but [G]now I [C]see', 
     '經典聖歌，適合初學者練習'),
    ('660e8400-e29b-41d4-a716-446655440001', 'House of the Rising Sun', 'The Animals', 'Am', 0, 75, '550e8400-e29b-41d4-a716-446655440000',
     '[Am]There is a [C]house in [D]New Or[F]leans
They [Am]call the [C]Rising [E]Sun
And it''s [Am]been the [C]ruin of [D]many a poor [F]boy
And [Am]God I [E]know I''m [Am]one',
     '經典民謠，Am調，適合中級學習者');

-- 插入一些常用和絃
INSERT INTO custom_chords (name, frets, fingers, created_by, is_public) VALUES 
    ('C', '{0,1,0,2,3,0}', '{0,1,0,2,3,0}', '550e8400-e29b-41d4-a716-446655440000', true),
    ('G', '{3,2,0,0,3,3}', '{3,2,0,0,4,4}', '550e8400-e29b-41d4-a716-446655440000', true),
    ('Am', '{0,0,2,2,1,0}', '{0,0,2,3,1,0}', '550e8400-e29b-41d4-a716-446655440000', true),
    ('F', '{1,1,3,3,2,1}', '{1,1,3,4,2,1}', '550e8400-e29b-41d4-a716-446655440000', true),
    ('Dm', '{-1,-1,0,2,3,1}', '{0,0,0,1,3,2}', '550e8400-e29b-41d4-a716-446655440000', true),
    ('E', '{0,2,2,1,0,0}', '{0,2,3,1,0,0}', '550e8400-e29b-41d4-a716-446655440000', true);

COMMIT;