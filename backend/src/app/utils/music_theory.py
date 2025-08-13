"""
Music theory utilities for chord transposition and musical calculations.
"""
import re
from typing import Dict, List, Optional, Tuple

# Musical constants
CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC_MAP = {
    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
}

# Common chord patterns
CHORD_PATTERNS = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    '7': [0, 4, 7, 10],
    'maj7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10],
    'dim7': [0, 3, 6, 9],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'add9': [0, 4, 7, 14],
    '6': [0, 4, 7, 9],
    'm6': [0, 3, 7, 9],
}

# Standard guitar tuning (low to high)
STANDARD_TUNING = ['E', 'A', 'D', 'G', 'B', 'E']


def normalize_chord_name(chord: str) -> str:
    """Normalize chord name by converting flats to sharps."""
    for flat, sharp in ENHARMONIC_MAP.items():
        chord = chord.replace(flat, sharp)
    return chord


def parse_chord(chord_str: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse a chord string into root, quality, and bass note.
    
    Examples:
    - "Am" -> ("A", "m", None)
    - "F#m7" -> ("F#", "m7", None)
    - "C/E" -> ("C", "", "E")
    - "Dm7/F" -> ("D", "m7", "F")
    """
    chord_str = normalize_chord_name(chord_str.strip())
    
    # Check for slash chord (bass note)
    bass_note = None
    if '/' in chord_str:
        chord_str, bass_note = chord_str.split('/', 1)
        bass_note = bass_note.strip()
    
    # Parse root note (including sharps)
    root_match = re.match(r'^([A-G]#?)', chord_str)
    if not root_match:
        raise ValueError(f"Invalid chord: {chord_str}")
    
    root = root_match.group(1)
    quality = chord_str[len(root):]
    
    return root, quality, bass_note


def transpose_note(note: str, semitones: int) -> str:
    """Transpose a single note by a number of semitones."""
    note = normalize_chord_name(note)
    
    if note not in CHROMATIC_SCALE:
        raise ValueError(f"Invalid note: {note}")
    
    current_index = CHROMATIC_SCALE.index(note)
    new_index = (current_index + semitones) % 12
    return CHROMATIC_SCALE[new_index]


def transpose_chord(chord_str: str, semitones: int) -> str:
    """
    Transpose a chord by a number of semitones.
    
    Args:
        chord_str: Original chord (e.g., "Am7", "F#dim/A")
        semitones: Number of semitones to transpose (positive = up, negative = down)
    
    Returns:
        Transposed chord string
    """
    try:
        root, quality, bass_note = parse_chord(chord_str)
        
        # Transpose root note
        new_root = transpose_note(root, semitones)
        
        # Transpose bass note if present
        new_bass_note = None
        if bass_note:
            new_bass_note = transpose_note(bass_note, semitones)
        
        # Reconstruct chord
        new_chord = new_root + quality
        if new_bass_note:
            new_chord += f"/{new_bass_note}"
        
        return new_chord
    
    except (ValueError, IndexError) as e:
        # If chord parsing fails, return original chord
        return chord_str


def get_key_semitone_difference(from_key: str, to_key: str) -> int:
    """
    Calculate semitone difference between two keys.
    
    Args:
        from_key: Original key (e.g., "C", "Am", "F#")
        to_key: Target key (e.g., "D", "Bm", "G")
    
    Returns:
        Number of semitones between keys
    """
    # Extract root note from key (ignore major/minor)
    from_root = re.match(r'^([A-G]#?)', normalize_chord_name(from_key))
    to_root = re.match(r'^([A-G]#?)', normalize_chord_name(to_key))
    
    if not from_root or not to_root:
        raise ValueError("Invalid key names")
    
    from_note = from_root.group(1)
    to_note = to_root.group(1)
    
    from_index = CHROMATIC_SCALE.index(from_note)
    to_index = CHROMATIC_SCALE.index(to_note)
    
    # Calculate shortest path (considering octave wrap)
    diff = (to_index - from_index) % 12
    if diff > 6:
        diff -= 12
    
    return diff


def transpose_chord_progression(chords: List[str], semitones: int) -> List[str]:
    """
    Transpose a list of chords by a number of semitones.
    
    Args:
        chords: List of chord strings
        semitones: Number of semitones to transpose
    
    Returns:
        List of transposed chords
    """
    return [transpose_chord(chord, semitones) for chord in chords]


def calculate_capo_transposition(original_key: str, capo_fret: int) -> str:
    """
    Calculate the effective key when using a capo.
    
    Args:
        original_key: The key the song is written in
        capo_fret: Fret position of capo (0 = no capo)
    
    Returns:
        The effective key with capo
    """
    if capo_fret == 0:
        return original_key
    
    # Extract root note from key
    root_match = re.match(r'^([A-G]#?)', normalize_chord_name(original_key))
    if not root_match:
        raise ValueError("Invalid key")
    
    root = root_match.group(1)
    suffix = original_key[len(root):]
    
    # Transpose root note up by capo frets
    new_root = transpose_note(root, capo_fret)
    
    return new_root + suffix


def suggest_capo_position(from_key: str, to_key: str) -> Optional[int]:
    """
    Suggest capo position to play in target key from original key.
    
    Args:
        from_key: Original key of the song
        to_key: Desired key to play in
    
    Returns:
        Capo fret position (1-12) or None if not practical
    """
    try:
        semitones = get_key_semitone_difference(from_key, to_key)
        
        # Capo can only raise pitch, not lower it
        if semitones < 0:
            semitones += 12
        
        # Practical capo range is 1-12 frets
        if 1 <= semitones <= 12:
            return semitones
        
        return None
    
    except ValueError:
        return None


def get_chord_intervals(chord_str: str) -> List[int]:
    """
    Get the intervals for a chord.
    
    Args:
        chord_str: Chord string (e.g., "Am7", "F#dim")
    
    Returns:
        List of intervals from root note
    """
    try:
        root, quality, bass_note = parse_chord(chord_str)
        
        # Look up chord pattern
        quality_clean = quality.lower().replace('maj', '').replace('min', 'm')
        
        if quality_clean in CHORD_PATTERNS:
            return CHORD_PATTERNS[quality_clean]
        elif quality_clean == '' or quality_clean == 'maj':
            return CHORD_PATTERNS['major']
        elif quality_clean == 'm':
            return CHORD_PATTERNS['minor']
        else:
            # Default to major if unknown
            return CHORD_PATTERNS['major']
    
    except ValueError:
        return CHORD_PATTERNS['major']


def extract_chords_from_text(text: str) -> List[str]:
    """
    Extract chord names from lyrics and chords text.
    
    Args:
        text: Text containing chords above lyrics
    
    Returns:
        List of unique chord names found
    """
    # Enhanced chord regex to match common chord patterns
    chord_pattern = r'\b([A-G]#?b?(?:maj|min|m|dim|aug|sus[24]?|add[9]?|[67]|maj7|m7|dim7|sus2|sus4|add9|6|m6|9|11|13)?(?:/[A-G]#?b?)?)\b'
    
    matches = re.findall(chord_pattern, text, re.IGNORECASE)
    
    # Clean and normalize chord names
    chords = []
    for match in matches:
        chord = match.strip()
        # Filter out common false positives
        if len(chord) >= 1 and not chord.lower() in ['a', 'i', 'am', 'is', 'as', 'me', 'go', 'be', 'do']:
            chords.append(normalize_chord_name(chord))
    
    return list(set(chords))  # Return unique chords


def validate_chord_name(chord_str: str) -> bool:
    """
    Validate if a string is a valid chord name.
    
    Args:
        chord_str: String to validate
    
    Returns:
        True if valid chord name, False otherwise
    """
    try:
        root, quality, bass_note = parse_chord(chord_str)
        
        # Check if root note is valid
        if root not in CHROMATIC_SCALE:
            return False
        
        # Check if bass note is valid (if present)
        if bass_note and bass_note not in CHROMATIC_SCALE:
            return False
        
        return True
    
    except (ValueError, IndexError):
        return False