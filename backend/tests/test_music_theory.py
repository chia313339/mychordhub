"""
Test music theory utilities.
"""
import pytest

from app.utils.music_theory import (
    calculate_capo_transposition,
    extract_chords_from_text,
    get_key_semitone_difference,
    parse_chord,
    suggest_capo_position,
    transpose_chord,
    transpose_chord_progression,
    validate_chord_name,
)


class TestChordParsing:
    """Test chord parsing functions."""
    
    def test_parse_simple_chords(self):
        """Test parsing simple chords."""
        assert parse_chord("C") == ("C", "", None)
        assert parse_chord("Am") == ("A", "m", None)
        assert parse_chord("F#") == ("F#", "", None)
        assert parse_chord("Bb7") == ("Bb", "7", None)
    
    def test_parse_slash_chords(self):
        """Test parsing slash chords."""
        assert parse_chord("C/E") == ("C", "", "E")
        assert parse_chord("Am/F") == ("A", "m", "F")
        assert parse_chord("D7/F#") == ("D", "7", "F#")
    
    def test_parse_complex_chords(self):
        """Test parsing complex chords."""
        assert parse_chord("Cmaj7") == ("C", "maj7", None)
        assert parse_chord("F#m7") == ("F#", "m7", None)
        assert parse_chord("Bdim") == ("B", "dim", None)


class TestTransposition:
    """Test chord transposition functions."""
    
    def test_transpose_simple_chords(self):
        """Test transposing simple chords."""
        assert transpose_chord("C", 2) == "D"
        assert transpose_chord("Am", 3) == "Cm"
        assert transpose_chord("F#", -1) == "F"
        assert transpose_chord("G", 5) == "C"
    
    def test_transpose_slash_chords(self):
        """Test transposing slash chords."""
        assert transpose_chord("C/E", 2) == "D/F#"
        assert transpose_chord("Am/F", -2) == "Gm/D#"
    
    def test_transpose_chord_progression(self):
        """Test transposing chord progressions."""
        chords = ["C", "Am", "F", "G"]
        transposed = transpose_chord_progression(chords, 2)
        assert transposed == ["D", "Bm", "G", "A"]
    
    def test_key_semitone_difference(self):
        """Test calculating semitone differences between keys."""
        assert get_key_semitone_difference("C", "D") == 2
        assert get_key_semitone_difference("C", "F") == 5
        assert get_key_semitone_difference("A", "C") == 3
        assert get_key_semitone_difference("F", "C") == -5


class TestCapoCalculations:
    """Test capo-related calculations."""
    
    def test_capo_transposition(self):
        """Test capo transposition calculations."""
        assert calculate_capo_transposition("C", 0) == "C"
        assert calculate_capo_transposition("C", 2) == "D"
        assert calculate_capo_transposition("Am", 3) == "Cm"
        assert calculate_capo_transposition("F", 5) == "A"
    
    def test_capo_suggestions(self):
        """Test capo position suggestions."""
        assert suggest_capo_position("C", "D") == 2
        assert suggest_capo_position("G", "A") == 2
        assert suggest_capo_position("C", "F") == 5
        assert suggest_capo_position("F", "C") is None  # Can't lower with capo


class TestChordValidation:
    """Test chord validation functions."""
    
    def test_valid_chords(self):
        """Test valid chord names."""
        valid_chords = ["C", "Am", "F#m7", "Bb", "Dm/F", "G7", "Cmaj7"]
        for chord in valid_chords:
            assert validate_chord_name(chord) is True
    
    def test_invalid_chords(self):
        """Test invalid chord names."""
        invalid_chords = ["H", "Xm", "Z7", "123", ""]
        for chord in invalid_chords:
            assert validate_chord_name(chord) is False


class TestChordExtraction:
    """Test chord extraction from text."""
    
    def test_extract_chords_from_lyrics(self):
        """Test extracting chords from lyrics text."""
        text = """
        C                Am
        Amazing grace how sweet the sound
        F               G           C
        That saved a wretch like me
        """
        chords = extract_chords_from_text(text)
        expected = ["C", "Am", "F", "G"]
        assert set(chords) == set(expected)
    
    def test_extract_complex_chords(self):
        """Test extracting complex chords."""
        text = "Cmaj7 F#m7 Bb7 Am/F G7sus4"
        chords = extract_chords_from_text(text)
        expected = ["Cmaj7", "F#m7", "Bb7", "Am/F", "G7sus4"]
        assert set(chords) == set(expected)