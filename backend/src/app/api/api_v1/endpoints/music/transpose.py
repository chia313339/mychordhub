"""
Chord transposition and key change endpoints.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.music_theory import (
    calculate_capo_transposition,
    extract_chords_from_text,
    get_key_semitone_difference,
    suggest_capo_position,
    transpose_chord,
    transpose_chord_progression,
    validate_chord_name,
)

router = APIRouter()


class TransposeRequest(BaseModel):
    """Request model for chord transposition."""
    chords: List[str]
    semitones: int


class TransposeResponse(BaseModel):
    """Response model for chord transposition."""
    original_chords: List[str]
    transposed_chords: List[str]
    semitones: int


class KeyChangeRequest(BaseModel):
    """Request model for key change."""
    original_key: str
    target_key: str
    chords: List[str]


class KeyChangeResponse(BaseModel):
    """Response model for key change."""
    original_key: str
    target_key: str
    semitones: int
    original_chords: List[str]
    transposed_chords: List[str]


class CapoSuggestionRequest(BaseModel):
    """Request model for capo suggestions."""
    original_key: str
    target_key: str


class CapoSuggestionResponse(BaseModel):
    """Response model for capo suggestions."""
    original_key: str
    target_key: str
    capo_fret: Optional[int]
    effective_key: Optional[str]


class LyricsTransposeRequest(BaseModel):
    """Request model for transposing chords in lyrics."""
    lyrics_and_chords: str
    semitones: int


class LyricsTransposeResponse(BaseModel):
    """Response model for transposed lyrics."""
    original_text: str
    transposed_text: str
    chords_found: List[str]
    transposed_chords: List[str]


@router.post("/transpose", response_model=TransposeResponse)
def transpose_chords(
    *,
    request: TransposeRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Transpose a list of chords by a number of semitones.
    """
    # Validate chord names
    invalid_chords = [chord for chord in request.chords if not validate_chord_name(chord)]
    if invalid_chords:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chord names: {', '.join(invalid_chords)}"
        )
    
    transposed_chords = transpose_chord_progression(request.chords, request.semitones)
    
    return TransposeResponse(
        original_chords=request.chords,
        transposed_chords=transposed_chords,
        semitones=request.semitones
    )


@router.post("/change-key", response_model=KeyChangeResponse)
def change_key(
    *,
    request: KeyChangeRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Change chords from one key to another.
    """
    try:
        semitones = get_key_semitone_difference(request.original_key, request.target_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Validate chord names
    invalid_chords = [chord for chord in request.chords if not validate_chord_name(chord)]
    if invalid_chords:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chord names: {', '.join(invalid_chords)}"
        )
    
    transposed_chords = transpose_chord_progression(request.chords, semitones)
    
    return KeyChangeResponse(
        original_key=request.original_key,
        target_key=request.target_key,
        semitones=semitones,
        original_chords=request.chords,
        transposed_chords=transposed_chords
    )


@router.post("/capo-suggestion", response_model=CapoSuggestionResponse)
def get_capo_suggestion(
    *,
    request: CapoSuggestionRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get capo position suggestion for key change.
    """
    capo_fret = suggest_capo_position(request.original_key, request.target_key)
    
    effective_key = None
    if capo_fret:
        try:
            effective_key = calculate_capo_transposition(request.original_key, capo_fret)
        except ValueError:
            pass
    
    return CapoSuggestionResponse(
        original_key=request.original_key,
        target_key=request.target_key,
        capo_fret=capo_fret,
        effective_key=effective_key
    )


@router.post("/transpose-lyrics", response_model=LyricsTransposeResponse)
def transpose_lyrics(
    *,
    request: LyricsTransposeRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Transpose chords found in lyrics and chord text.
    """
    # Extract chords from text
    chords_found = extract_chords_from_text(request.lyrics_and_chords)
    
    # Transpose each chord
    transposed_chords = transpose_chord_progression(chords_found, request.semitones)
    
    # Replace chords in text
    transposed_text = request.lyrics_and_chords
    for original, transposed in zip(chords_found, transposed_chords):
        # Replace exact word matches to avoid partial replacements
        import re
        pattern = r'\b' + re.escape(original) + r'\b'
        transposed_text = re.sub(pattern, transposed, transposed_text, flags=re.IGNORECASE)
    
    return LyricsTransposeResponse(
        original_text=request.lyrics_and_chords,
        transposed_text=transposed_text,
        chords_found=chords_found,
        transposed_chords=transposed_chords
    )


@router.get("/validate-chord")
def validate_chord(
    chord: str = Query(..., description="Chord name to validate"),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Validate a chord name.
    """
    is_valid = validate_chord_name(chord)
    
    result = {
        "chord": chord,
        "is_valid": is_valid
    }
    
    if is_valid:
        try:
            from app.utils.music_theory import parse_chord, get_chord_intervals
            root, quality, bass_note = parse_chord(chord)
            intervals = get_chord_intervals(chord)
            
            result.update({
                "root": root,
                "quality": quality,
                "bass_note": bass_note,
                "intervals": intervals
            })
        except Exception:
            pass
    
    return result


@router.get("/extract-chords")
def extract_chords(
    text: str = Query(..., description="Text to extract chords from"),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Extract chord names from text.
    """
    chords = extract_chords_from_text(text)
    
    return {
        "text": text,
        "chords_found": chords,
        "chord_count": len(chords)
    }