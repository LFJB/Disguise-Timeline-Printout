"""
Script executed INSIDE Disguise Designer (Python 2.7).
Returns a JSON string with all timeline data.
DO NOT run this directly — it is sent to Designer via the plugin API.
"""

import json


def get_field_value(layer, field_name):
    """Safely retrieve a field value from a layer."""
    try:
        seq = layer.findSequence(field_name)
        if seq is None:
            return None
        ks = seq.sequence
        if ks is None:
            return None
        # Collect all keyframe values
        keys = []
        try:
            for kf in ks:
                keys.append({
                    "beat": float(kf.beat),
                    "value": str(kf.value),
                })
        except Exception:
            pass
        return keys if keys else None
    except Exception:
        return None


def get_layer_data(layer):
    """Extract all meaningful data from a layer."""
    data = {
        "name": str(layer.name) if layer.name else "",
        "enabled": bool(layer.enabled),
        "t_start": float(layer.tStart),
        "t_end": float(layer.tEnd),
        "t_length": float(layer.tLength),
        "module_type": "",
        "fields": {},
        "resource": None,
    }

    # Module type
    try:
        data["module_type"] = str(layer.moduleType())
    except Exception:
        try:
            data["module_type"] = str(type(layer.module).__name__)
        except Exception:
            data["module_type"] = "unknown"

    # Common fields to inspect
    common_fields = [
        "opacity", "brightness", "contrast", "saturation",
        "r", "g", "b", "a",
        "x", "y", "z", "scale", "rotation",
        "width", "height",
        "blend", "blendMode",
        "mapping", "mapName",
        "text",
        "speed", "volume",
        "fit", "fitMode",
        "loop", "loopMode",
    ]

    for field_name in common_fields:
        value = get_field_value(layer, field_name)
        if value is not None:
            data["fields"][field_name] = value

    # Try to get resource / content path
    try:
        mod = layer.module
        if hasattr(mod, "video") and mod.video is not None:
            data["resource"] = str(mod.video)
        elif hasattr(mod, "resource") and mod.resource is not None:
            data["resource"] = str(mod.resource)
        elif hasattr(mod, "file") and mod.file is not None:
            data["resource"] = str(mod.file)
    except Exception:
        pass

    # Try to enumerate all available sequences/fields
    try:
        if hasattr(layer, "fields"):
            for fname in layer.fields:
                if fname not in data["fields"]:
                    value = get_field_value(layer, fname)
                    if value is not None:
                        data["fields"][fname] = value
    except Exception:
        pass

    return data


def get_cue_data(track):
    """Extract all cues from a track."""
    cues = []
    try:
        beats = track.cueBeats()
        for beat in beats:
            cue_info = {
                "beat": float(beat),
                "name": "",
                "note": "",
                "time_seconds": float(track.beatToTime(beat)),
            }
            # Try to get cue name/note
            try:
                note = track.noteAtBeat(beat)
                cue_info["note"] = str(note) if note else ""
            except Exception:
                pass
            try:
                cue = track.cueAtBeat(beat)
                if cue is not None:
                    try:
                        cue_info["name"] = str(cue.name) if hasattr(cue, "name") else ""
                    except Exception:
                        pass
                    try:
                        cue_info["note"] = str(cue.note) if hasattr(cue, "note") else cue_info["note"]
                    except Exception:
                        pass
                    try:
                        cue_info["type"] = str(cue.type) if hasattr(cue, "type") else ""
                    except Exception:
                        pass
            except Exception:
                pass
            cues.append(cue_info)
    except Exception as e:
        cues.append({"error": str(e)})
    return cues


def get_track_data(track):
    """Extract all data from a single track."""
    data = {
        "name": "",
        "length_in_beats": 0.0,
        "cues": [],
        "layers": [],
    }

    try:
        data["name"] = str(track.name) if hasattr(track, "name") else "track"
    except Exception:
        pass

    try:
        data["length_in_beats"] = float(track.lengthInBeats)
    except Exception:
        pass

    # Cues
    data["cues"] = get_cue_data(track)

    # Layers
    try:
        for layer in track.layers:
            layer_data = get_layer_data(layer)
            data["layers"].append(layer_data)
    except Exception as e:
        data["layers_error"] = str(e)

    return data


def extract_all_tracks():
    """Main entry point: extract all tracks from the project."""
    result = {
        "tracks": [],
        "project": {},
        "errors": [],
    }

    # Try to get project name
    try:
        result["project"]["name"] = str(state.project.name) if hasattr(state, "project") else ""
    except Exception:
        pass

    # Strategy 1: all tracks via state
    tracks_found = False
    try:
        if hasattr(state, "tracks"):
            for track in state.tracks:
                result["tracks"].append(get_track_data(track))
            tracks_found = True
    except Exception as e:
        result["errors"].append("state.tracks: " + str(e))

    # Strategy 2: tracks via guisystem / crossfader
    if not tracks_found:
        try:
            if hasattr(guisystem, "tracks"):
                for track in guisystem.tracks:
                    result["tracks"].append(get_track_data(track))
                tracks_found = True
        except Exception as e:
            result["errors"].append("guisystem.tracks: " + str(e))

    # Strategy 3: single current track only
    if not tracks_found:
        try:
            track = guisystem.track
            result["tracks"].append(get_track_data(track))
            tracks_found = True
        except Exception as e:
            result["errors"].append("guisystem.track: " + str(e))

    # Strategy 4: state.track
    if not tracks_found:
        try:
            track = state.track
            result["tracks"].append(get_track_data(track))
        except Exception as e:
            result["errors"].append("state.track: " + str(e))

    return json.dumps(result)


# Execute and return
extract_all_tracks()
