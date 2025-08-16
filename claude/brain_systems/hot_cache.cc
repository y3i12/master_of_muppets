// Hot Cache v2.0 - Working memory for active graph operations
// Ultra-fast lookups for hardware/software graph traversal
// Load: Include this for instant graph access during work sessions

#include <stdint.h>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>

// Hot Node Types (bit-packed for cache efficiency)
#define NT_IC        0x01  // Integrated circuit
#define NT_RESISTOR  0x02  // Resistor  
#define NT_CAPACITOR 0x04  // Capacitor
#define NT_CONNECTOR 0x08  // Connector/jack
#define NT_MODULE    0x10  // Module/sheet
#define NT_CLASS     0x20  // C++ class
#define NT_FUNCTION  0x40  // Function
#define NT_THREAD    0x80  // Thread

// Working Set Focus (what we're actively working on)
#define WS_POWER     0x01  // Power distribution focus
#define WS_SIGNAL    0x02  // Signal path focus  
#define WS_THERMAL   0x04  // Thermal management
#define WS_I2C       0x08  // I2C bus focus
#define WS_THREADS   0x10  // Threading focus
#define WS_BUFFERS   0x20  // Buffer management
#define WS_REALTIME  0x40  // Real-time path
#define WS_PLACEMENT 0x80  // PCB placement focus

// Hot cache for immediate component lookups
struct HotComponent {
    uint32_t id;
    uint8_t  type;
    uint8_t  criticality;  // 0-255
    uint16_t connections;  // Bit mask of connected components
    float    x, y;         // Placement coordinates (if known)
    uint32_t props;        // Packed properties
};

// Critical path cache (0.1ms lookup time)
struct CriticalPath {
    uint8_t  length;
    uint32_t nodes[8];     // Max 8 hops for critical paths
    float    total_weight;
    uint8_t  path_type;    // Signal, power, thermal, etc.
};

// Working memory banks (think CPU cache levels)
namespace WorkingCache {
    
    // L1 Cache: Currently focused components (16 slots)
    HotComponent l1_cache[16];
    uint8_t l1_size = 0;
    uint8_t l1_focus = WS_PLACEMENT;  // Current working set
    
    // L2 Cache: Recently accessed paths (64 paths)
    CriticalPath l2_paths[64];
    uint8_t l2_size = 0;
    
    // L3 Cache: Frequently used lookups (256 entries)
    std::unordered_map<uint32_t, uint32_t> l3_lookup;
    
    // Working set state
    uint32_t focus_center[4];     // Up to 4 center components
    uint8_t  focus_radius = 2;    // Radius of current focus
    uint64_t focus_timestamp;     // When focus was set
    
    // Delta tracking (changes since last git sync)
    std::unordered_set<uint32_t> dirty_hw;
    std::unordered_set<uint32_t> dirty_sw;
    char git_revision[8];         // Short git hash
    
    // Hot functions for active work
    inline bool in_focus(uint32_t component_id) {
        for (int i = 0; i < 4; i++) {
            if (focus_center[i] == component_id) return true;
        }
        return false;
    }
    
    inline void mark_dirty(uint32_t id, bool is_hardware = true) {
        if (is_hardware) dirty_hw.insert(id);
        else dirty_sw.insert(id);
    }
    
    inline void set_focus(uint32_t* centers, uint8_t count, uint8_t mode) {
        l1_focus = mode;
        for (int i = 0; i < 4 && i < count; i++) {
            focus_center[i] = centers[i];
        }
        focus_timestamp = __builtin_ia32_rdtsc();  // Timestamp
    }
    
    // Cache population from JSON (called once per session)
    void load_from_persistent();
    
    // Hot path finder (breadth-first, cached)
    CriticalPath* find_path(uint32_t start, uint32_t end, uint8_t path_type);
    
    // Working set operations
    void focus_on_placement(uint32_t* components, uint8_t count);
    void focus_on_signal_path(uint32_t start, uint32_t end);
    void focus_on_power_zone(uint8_t zone_id);
    
    // Sync operations
    void sync_to_git(const char* revision);
    uint32_t get_dirty_count() { return dirty_hw.size() + dirty_sw.size(); }
}

// Instant lookup tables (populated from cognitive_core.json)
namespace QuickRef {
    // Hardware shortcuts
    const uint32_t DAC1_AD5593R = 0x5593001;
    const uint32_t DAC2_AD5593R = 0x5593002;  
    const uint32_t AMP1_TL074   = 0x7074001;
    const uint32_t AMP2_TL074   = 0x7074002;
    const uint32_t AMP3_TL074   = 0x7074003;
    const uint32_t AMP4_TL074   = 0x7074004;
    const uint32_t TEENSY_41    = 0x4100001;
    
    // Software shortcuts
    const uint32_t DR_TEETH_CLASS     = 0x8001001;
    const uint32_t ELECTRIC_MAYHEM    = 0x8002001;
    const uint32_t AD5593R_DRIVER     = 0x8003001;
    const uint32_t INPUT_BUFFER       = 0x8004001;
    const uint32_t OUTPUT_BUFFER      = 0x8004002;
    
    // Critical paths (pre-computed)
    const uint32_t PATH_USB_TO_DAC[]  = {TEENSY_41, DR_TEETH_CLASS, ELECTRIC_MAYHEM, DAC1_AD5593R};
    const uint32_t PATH_DAC_TO_OUT[]  = {DAC1_AD5593R, AMP1_TL074, 0x9001001}; // Output jack
    
    // Zone definitions
    const uint32_t POWER_ZONE_DIGITAL[] = {TEENSY_41, DR_TEETH_CLASS};
    const uint32_t POWER_ZONE_ANALOG[]  = {DAC1_AD5593R, DAC2_AD5593R, AMP1_TL074, AMP2_TL074};
    const uint32_t THERMAL_HOT_ZONE[]   = {AMP1_TL074, AMP2_TL074, AMP3_TL074, AMP4_TL074};
}

// Session working state (gets updated during active work)
struct SessionState {
    uint8_t  current_season = 0x02;      // Season 02
    uint8_t  current_episode = 0x01;     // Episode 01
    uint8_t  focus_mode = WS_PLACEMENT;  // Currently focusing on PCB placement
    uint32_t session_start_time;
    uint32_t operations_count = 0;
    
    // Performance counters
    uint32_t cache_hits = 0;
    uint32_t cache_misses = 0;
    uint32_t path_queries = 0;
    uint32_t focus_changes = 0;
    
    inline float cache_hit_rate() { 
        return (float)cache_hits / (cache_hits + cache_misses); 
    }
};

// Macro for instant working cache initialization
#define INIT_HOT_CACHE() \
    WorkingCache::set_focus(QuickRef::POWER_ZONE_ANALOG, 4, WS_PLACEMENT); \
    printf("Hot cache ready - Focus: PCB Placement, Components: %d\n", 4)

// Performance instrumented operations
#define HOT_LOOKUP(id) \
    (WorkingCache::in_focus(id) ? \
     (session.cache_hits++, true) : \
     (session.cache_misses++, false))

extern SessionState session;