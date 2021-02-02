import colorsys
import struct


class FieldBase:
    def _get_string(self, raw):
        return raw.split(b'\x00')[0].decode()


class FirmwareVersionField(FieldBase):
    """
    Data from the `_ver` field. This stores the major/minor firmware version numbers

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      2    u16    Major version
    2      2    u16    Minor version
    ====== ==== ====== ===========

    After parsing:

    :ivar major: Major firmware version
    :ivar minor: Minor firmware version
    """

    def __init__(self, raw):
        """
        :param raw:
        """
        self.raw = raw
        self.major, self.minor = struct.unpack('>HH', raw)
        self.version = "{}.{}".format(self.major, self.minor)

    def __repr__(self):
        return '<firmware-version {}>'.format(self.version)


class ProductNameField(FieldBase):
    """
    Data from the `_pin` field. This stores the product name of the mixer

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      44   char[] Product name
    ====== ==== ====== ===========

    After parsing:

    :ivar name: User friendly product name
    """

    def __init__(self, raw):
        self.raw = raw
        self.name = self._get_string(raw)

    def __repr__(self):
        return '<product-name {}>'.format(self.name)


class MixerEffectConfigField(FieldBase):
    """
    Data from the `_MeC` field. This stores basic info about the M/E units.

    The mixer will send multiple fields, one for each M/E unit.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    u8     Number of keyers on this M/E
    2      2    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar name: User friendly product name
    """

    def __init__(self, raw):
        self.raw = raw
        self.me, self.keyers = struct.unpack('>2B2x', raw)

    def __repr__(self):
        return '<mixer-effect-config m/e {}: keyers={}>'.format(self.me, self.keyers)


class MediaplayerSlotsField(FieldBase):
    """
    Data from the `_mpl` field. This stores basic info about the mediaplayer slots.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     Number of still slots
    1      1    u8     Number of clip slots
    2      2    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar name: User friendly product name
    """

    def __init__(self, raw):
        self.raw = raw
        self.stills, self.clips = struct.unpack('>2B2x', raw)

    def __repr__(self):
        return '<mediaplayer-slots: stills={} clips={}>'.format(self.stills, self.clips)


class VideoModeField(FieldBase):
    """
    Data from the `VidM` field. This sets the video standard the mixer operates on internally.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     Video mode
    1      3    ?      unknown
    ====== ==== ====== ===========

    The `Video mode` is an enum of these values:

    === ==========
    Key Video mode
    === ==========
    0   NTSC (525i59.94)
    1   PAL (625i50)
    2   NTSC widescreen (525i59.94)
    3   PAL widescreen (625i50)
    4   720p50
    5   720p59.94
    6   1080i50
    7   1080i59.94
    8   1080p23.98
    9   1080p24
    10  1080p25
    11  1080p29.97
    12  1080p50
    13  1080p59.94
    14  4k23.98
    15  4k24
    16  4k25
    17  4k29.97
    26  1080p30
    27  1080p60
    === ==========

    After parsing:

    :ivar mode: mode number
    :ivar resolution: vertical resolution of the mode
    :ivar interlaced: the current mode is interlaced
    :ivar rate: refresh rate of the mode
    """

    def __init__(self, raw):
        self.raw = raw
        self.mode, = struct.unpack('>1B3x', raw)

        modes = {
            0: (525, True, 59.94),
            1: (625, True, 50),
            2: (525, True, 59.94),
            3: (625, True, 50),
            4: (720, False, 50),
            5: (720, False, 59.94),
            6: (1080, True, 50),
            7: (1080, True, 59.94),
            8: (1080, False, 23.98),
            9: (1080, False, 24),
            10: (1080, False, 25),
            11: (1080, False, 29.97),
            12: (1080, False, 50),
            13: (1080, False, 59.94),
            14: (2160, False, 23.98),
            15: (2160, False, 24),
            16: (2160, False, 25),
            17: (2160, False, 29.97),
            26: (1080, False, 30),
            27: (1080, False, 60),
        }

        if self.mode in modes:
            self.resolution = modes[self.mode][0]
            self.interlaced = modes[self.mode][1]
            self.rate = modes[self.mode][2]

    def get_label(self):
        if self.resolution is None:
            return 'unknown [{}]'.format(self.mode)

        pi = 'p'
        if self.interlaced:
            pi = 'i'
        return '{}{}{}'.format(self.resolution, pi, self.rate)

    def __repr__(self):
        return '<video-mode: mode={}: {}>'.format(self.mode, self.get_label())


class InputPropertiesField(FieldBase):
    """
    Data from the `InPr` field. This stores information about all the internal and external inputs.

    The mixer will send multiple fields, one for each input

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      2    u16    Source index
    2      20   char[] Long name
    22     4    char[] Short name for button
    26     1    u8     Source category 0=input 1=output
    27     1    u8     ? bitfield
    28     1    u8     same as byte 26
    29     1    u8     port
    30     1    u8     same as byte 26
    31     1    u8     same as byte 29
    32     1    u8     port type
    33     1    u8     bitfield
    34     1    u8     bitfield
    35     1    u8     direction
    ====== ==== ====== ===========

    ===== =========
    value port type
    ===== =========
    0     external
    1     black
    2     color bars
    3     color generator
    4     media player
    5     media player key
    6     supersource
    7     passthrough
    128   M/E output
    129   AUX output
    ===== =========

    ===== ===============
    value available ports
    ===== ===============
    0     SDI
    1     HDMI
    2     Component
    3     Composite
    4     S/Video
    ===== ===============

    ===== =============
    value selected port
    ===== =============
    0     internal
    1     SDI
    2     HDMI
    3     Composite
    4     Component
    5     S/Video
    ===== =============

    After parsing:

    :ivar index: Source index
    :ivar name: Long name
    :ivar short_name: Short name for button
    :ivar port_type: Integer describing the port type
    :ivar available_aux: Source can be routed to AUX
    :ivar available_multiview: Source can be routed to multiview
    :ivar available_supersource_art: Source can be routed to supersource
    :ivar available_supersource_box: Source can be routed to supersource
    :ivar available_key_source: Source can be used as keyer key source
    :ivar available_me1: Source can be routed to M/E 1
    :ivar available_me2: Source can be routed to M/E 2
    """

    PORT_EXTERNAL = 0
    PORT_BLACK = 1
    PORT_BARS = 2
    PORT_COLOR = 3
    PORT_MEDIAPLAYER = 4
    PORT_MEDIAPLAYER_KEY = 5
    PORT_SUPERSOURCE = 6
    PORT_PASSTHROUGH = 7
    PORT_ME_OUTPUT = 128
    PORT_AUX_OUTPUT = 129

    def __init__(self, raw):
        self.raw = raw
        fields = struct.unpack('>H 20s 4s 10B', raw)
        self.index = fields[0]
        self.name = self._get_string(fields[1])
        self.short_name = self._get_string(fields[2])
        self.source_category = fields[3]
        self.port_type = fields[9]
        self.source_ports = fields[6]

        self.available_aux = fields[11] & (1 << 0) != 0
        self.available_multiview = fields[11] & (1 << 1) != 0
        self.available_supersource_art = fields[11] & (1 << 2) != 0
        self.available_supersource_box = fields[11] & (1 << 3) != 0
        self.available_key_source = fields[11] & (1 << 4) != 0

        self.available_me1 = fields[12] & (1 << 0) != 0
        self.available_me2 = fields[12] & (1 << 1) != 0

    def __repr__(self):
        return '<input-properties: index={} name={} button={}>'.format(self.index, self.name, self.short_name)


class ProgramBusInputField(FieldBase):
    """
    Data from the `PrgI` field. This represents the active channel on the program bus of the specific M/E unit.

    The mixer will send a field for every M/E unit in the mixer.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    ?      unknown
    2      2    u16    Source index
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar source: Input source index, refers to an InputPropertiesField index
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.source = struct.unpack('>BxH', raw)

    def __repr__(self):
        return '<program-bus-input: me={} source={}>'.format(self.index, self.source)


class PreviewBusInputField(FieldBase):
    """
    Data from the `PrvI` field. This represents the active channel on the preview bus of the specific M/E unit.

    The mixer will send a field for every M/E unit in the mixer.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    ?      unknown
    2      2    u16    Source index
    4      1    u8     1 if preview is mixed in program during a transition
    5      3    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar source: Input source index, refers to an InputPropertiesField index
    :ivar in_program: Preview source is mixed into progam
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.source, in_program = struct.unpack('>B x H B 3x', raw)
        self.in_program = in_program == 1

    def __repr__(self):
        in_program = ''
        if self.in_program:
            in_program = ' in-program'
        return '<preview-bus-input: me={} source={}{}>'.format(self.index, self.source, in_program)


class TransitionSettingsField(FieldBase):
    """
    Data from the `TrSS` field. This stores the config of the "Next transition" and "Transition style" blocks on the
    control panels.

    The mixer will send a field for every M/E unit in the mixer.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    u8     Transition style
    2      1    u8     Next transition layers
    3      1    u8     Next transition style
    4      1    u8     Next transition next transition layers
    ====== ==== ====== ===========

    There are two sets of style/layer settings. The first set is the active transition settings. The second one
    will store the transitions settings if you change any of them while a transition is active. These settings will be
    applied as soon as the transition ends. This is signified by blinking transition settings buttons in the official
    control panels.

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar style: Active transition style
    :ivar style_next: Transition style for next transition
    :ivar next_transition_bkgd: Next transition will affect the background layer
    :ivar next_transition_key1: Next transition will affect the upstream key 1 layer
    :ivar next_transition_key2: Next transition will affect the upstream key 2 layer
    :ivar next_transition_key3: Next transition will affect the upstream key 3 layer
    :ivar next_transition_key4: Next transition will affect the upstream key 4 layer
    :ivar next_transition_bkgd_next: Next transition (after current) will affect the background layer
    :ivar next_transition_key1_next: Next transition (after current) will affect the upstream key 1 layer
    :ivar next_transition_key2_next: Next transition (after current) will affect the upstream key 2 layer
    :ivar next_transition_key3_next: Next transition (after current) will affect the upstream key 3 layer
    :ivar next_transition_key4_next: Next transition (after current) will affect the upstream key 4 layer

    """

    STYLE_MIX = 0
    STYLE_DIP = 1
    STYLE_WIPE = 2
    STYLE_DVE = 3
    STYLE_STING = 4

    def __init__(self, raw):
        self.raw = raw
        self.index, self.style, nt, self.style_next, ntn = struct.unpack('>B 2B 2B 3x', raw)

        self.next_transition_bkgd = nt & (1 << 0) != 0
        self.next_transition_key1 = nt & (1 << 1) != 0
        self.next_transition_key2 = nt & (1 << 2) != 0
        self.next_transition_key3 = nt & (1 << 3) != 0
        self.next_transition_key4 = nt & (1 << 4) != 0

        self.next_transition_bkgd_next = ntn & (1 << 0) != 0
        self.next_transition_key1_next = ntn & (1 << 1) != 0
        self.next_transition_key2_next = ntn & (1 << 2) != 0
        self.next_transition_key3_next = ntn & (1 << 3) != 0
        self.next_transition_key4_next = ntn & (1 << 4) != 0

    def __repr__(self):
        return '<transition-settings: me={} style={}>'.format(self.index, self.style)


class TransitionPreviewField(FieldBase):
    """
    Data from the `TsPr` field. This represents the state of the "PREV TRANS" button on the mixer.

    The mixer will send a field for every M/E unit in the mixer.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    bool   Enabled
    2      2    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar enabled: True if the transition preview is enabled
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.enabled = struct.unpack('>B ? 2x', raw)

    def __repr__(self):
        return '<transition-preview: me={} enabled={}>'.format(self.index, self.enabled)


class TransitionPositionField(FieldBase):
    """
    Data from the `TrPs` field. This represents the state of the transition T-handle position

    The mixer will send a field for every M/E unit in the mixer.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    bool   In transition
    2      1    u8     Frames remaining
    3      1    ?      unknown
    4      2    u16    Position
    6      1    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar in_transition: True if the transition is active
    :ivar frames_remaining: Number of frames left to complete the transition on auto
    :ivar position: Position of the transition, 0.0 - 1.0
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.in_transition, self.frames_remaining, position = struct.unpack('>B ? B x H 2x', raw)
        self.position = position / 9999.0

    def __repr__(self):
        return '<transition-position: me={} frames-remaining={} position={:02f}>'.format(self.index,
                                                                                         self.frames_remaining,
                                                                                         self.position)


class TallyIndexField(FieldBase):
    """
    Data from the `TlIn`. This is the status of the tally light for every input in order of index number.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      2    u16    Total of tally lights
    n      1    u8     Bitfield, bit0=PROGRAM, bit1=PREVIEW, repeated for every tally light
    ====== ==== ====== ===========

    After parsing:

    :ivar num: number of tally lights
    :ivar tally: List of tally values, every tally light is represented as a tuple with 2 booleans for PROGRAM and PREVIEW
    """

    def __init__(self, raw):
        self.raw = raw
        offset = 0
        self.num, = struct.unpack_from('>H', raw, offset)
        self.tally = []
        offset += 2
        for i in range(0, self.num):
            tally, = struct.unpack_from('>B', raw, offset)
            self.tally.append((tally & 1 != 0, tally & 2 != 0))
            offset += 1

    def __repr__(self):
        return '<tally-index: num={}, val={}>'.format(self.num, self.tally)


class TallySourceField(FieldBase):
    """
    Data from the `TlSr`. This is the status of the tally light for every input, but indexed on source index

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      2    u16    Total of tally lights
    n      2    u16    Source index for this tally light
    n+2    1    u8     Bitfield, bit0=PROGRAM, bit1=PREVIEW
    ====== ==== ====== ===========

    After parsing:

    :ivar num: number of tally lights
    :ivar tally: Dict of tally lights, every tally light is represented as a tuple with 2 booleans for PROGRAM and PREVIEW
    """

    def __init__(self, raw):
        self.raw = raw
        offset = 0
        self.num, = struct.unpack_from('>H', raw, offset)
        self.tally = {}
        offset += 2
        for i in range(0, self.num):
            source, tally, = struct.unpack_from('>HB', raw, offset)
            self.tally[source] = (tally & 1 != 0, tally & 2 != 0)
            offset += 3

    def __repr__(self):
        return '<tally-index: num={}, val={}>'.format(self.num, self.tally)


class KeyOnAirField(FieldBase):
    """
    Data from the `KeOn`. This is the on-air state of the upstream keyers

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    u8     Keyer index
    2      1    bool   On-air
    3      1    ?      unknown
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar keyer: Upstream keyer number
    :ivar enabled: Wether the keyer is on-air
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.keyer, self.enabled = struct.unpack('>BB?x', raw)

    def __repr__(self):
        return '<key-on-air: me={}, keyer={}, enabled={}>'.format(self.index, self.keyer, self.enabled)


class ColorGeneratorField(FieldBase):
    """
    Data from the `ColV`. This is color set in the color generators of the mixer

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     Color generator index
    1      1    ?      unknown
    2      2    u16    Hue [0-3599]
    4      2    u16    Saturation [0-1000]
    6      2    u16    Luma [0-1000]
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar keyer: Upstream keyer number
    :ivar enabled: Wether the keyer is on-air
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.hue, self.saturation, self.luma = struct.unpack('>Bx 3H', raw)
        self.hue = self.hue / 10.0
        self.saturation = self.saturation / 1000.0
        self.luma = self.luma / 1000.0

    def get_rgb(self):
        return colorsys.hls_to_rgb(self.hue / 360.0, self.luma, self.saturation)

    def __repr__(self):
        return '<color-generator: index={}, hue={} saturation={} luma={}>'.format(self.index, self.hue, self.saturation,
                                                                                  self.luma)


class FadeToBlackStateField(FieldBase):
    """
    Data from the `FtbS`. This contains the information about the fade-to-black transition.

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     M/E index
    1      1    bool   Fade to black done
    2      1    bool   Fade to black is in transition
    3      1    u8     Frames remaining in transition
    ====== ==== ====== ===========

    After parsing:

    :ivar index: M/E index in the mixer
    :ivar done: Fade to black is completely done (blinking button state in the control panel)
    :ivar transitioning: Fade to black is fading, (Solid red in control panel)
    :ivar frames_remaining: Frames remaining in the transition
    """

    def __init__(self, raw):
        self.raw = raw
        self.index, self.done, self.transitioning, self.frames_remaining = struct.unpack('>B??B', raw)

    def __repr__(self):
        return '<fade-to-black-state: me={}, done={}, transitioning={}, frames-remaining={}>'.format(self.index,
                                                                                                     self.done,
                                                                                                     self.transitioning,
                                                                                                     self.frames_remaining)


class MediaplayerFileInfoField(FieldBase):
    """
    Data from the `MPfe`. This is the metadata about a single frame slot in the mediaplayer

    ====== ==== ====== ===========
    Offset Size Type   Description
    ====== ==== ====== ===========
    0      1    u8     type
    1      1    ?      unknown
    2      2    u16    index
    4      1    bool   is used
    5      16   char[] hash
    21     2    ?      unknown
    23     ?    string name of the slot, first byte is number of characters
    ====== ==== ====== ===========

    After parsing:

    :ivar index: Slot index
    :ivar type: Slot type, 0=still
    :ivar is_used: Slot contains data
    :ivar hash: 16-byte md5 hash of the slot data
    :ivar name: Name of the content in the slot
    """

    def __init__(self, raw):
        self.raw = raw
        namelen = len(raw) - 23
        self.type, self.index, self.is_used, self.hash, self.name = struct.unpack('>Bx H ? 16s 2x {}p'.format(namelen),
                                                                                  raw)

    def __repr__(self):
        return '<mediaplayer-file-info: type={} index={} used={} name={}>'.format(self.type, self.index, self.is_used,
                                                                                  self.name)
