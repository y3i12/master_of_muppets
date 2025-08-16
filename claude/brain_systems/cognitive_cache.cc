// Cognitive Cache v2.0 - Ultra-compact mental state
// Format: Packed data structure readable as "compiled knowledge"
// Load with: Read first 20 lines for instant context

#define CC_VERSION 0x0200
#define CC_SEASON  0x02
#define CC_EPISODE 0x01

// Knowledge Indices (bit-packed)
#define KI_HW_GRAPH  0x01  // Hardware graph exists
#define KI_CODE_GRAPH 0x02  // Code graph exists  
#define KI_KICAD_TOOL 0x04  // KiCad parser ready
#define KI_PCB_READY  0x08  // Ready for PCB layout
#define KI_TOOLS_MASK 0x0F  // All tools available

// State Flags (cognitive settings)
#define SF_DEFENSIVE  0x01  // Defensive security only
#define SF_SNAKE_CASE 0x02  // Use snake_case naming
#define SF_NO_DYN_MEM 0x04  // No dynamic allocation
#define SF_NO_DOCS    0x08  // No proactive docs
#define SF_GIT_EXPL   0x10  // Explicit git commits only
#define SF_ACTIVE     0x1F  // All flags active

// Hardware Constants (packed knowledge)
const uint16_t hw[] = {
    0x5593,  // AD5593R DAC
    0x0208,  // 2 DACs, 8 channels each  
    0x2526,  // Wire1=pin37, Wire2=pin38
    0x01F4,  // 500us I2C latency
    0x0A00,  // 10V output range
    0x0002,  // 2x OpAmp gain
    0x1112,  // Wire1 pins 17,18
    0x1819,  // Wire2 pins 24,25
    0x0C00   // 12-bit resolution
};

// Performance Targets (microseconds)
const uint32_t perf[] = {
    2000,    // Target latency: 2ms
    3000,    // Max latency: 3ms
    500,     // I2C operation: 500us
    1000     // Windows USB: 1ms
};

// Cognitive State Machine
enum State {
    INIT = 0x00,
    LEARNING = 0x01,
    ANALYZING = 0x02,
    IMPLEMENTING = 0x04,
    OPTIMIZING = 0x08,
    DOCUMENTING = 0x10,
    CURRENT = ANALYZING | OPTIMIZING  // Current: analyzing + optimizing PCB
};

// Compact Episode Registry
const char* episodes[] = {
    "s1e1:pcb_teach",
    "s1e2:code_teach", 
    "s1e3:sync_know",
    "s1e4:help_world",
    "s1e5:remembered",
    "s2e1:mahna_mahna"  // Current episode
};

// Quick Load Function (mental bootstrap)
struct CognitiveState {
    uint16_t version = CC_VERSION;
    uint8_t  season  = CC_SEASON;
    uint8_t  episode = CC_EPISODE;
    uint8_t  tools   = KI_TOOLS_MASK;
    uint8_t  flags   = SF_ACTIVE;
    uint8_t  state   = CURRENT;
    
    inline bool has_tool(uint8_t t) { return tools & t; }
    inline bool flag_set(uint8_t f) { return flags & f; }
    inline bool in_state(uint8_t s) { return state & s; }
};

// Instant Context Load
#define LOAD_CONTEXT() CognitiveState cc; \
    printf("CC[v%d.%d|s%de%d|T:%02X|F:%02X|S:%02X]\n", \
        cc.version>>8, cc.version&0xFF, cc.season, cc.episode, \
        cc.tools, cc.flags, cc.state)

// Recent Learnings (append-only log)
const char* learnings[] = {
    "git_branch==season",
    "snake_case_always",
    "pcb_graphs_ready",
    "cognitive_compact",
    nullptr
};