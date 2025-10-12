#pragma once

/**
 * @file scoped_lock.h
 * @brief RAII mutex lock guard for exception-safe locking
 * 
 * Provides automatic mutex unlock on scope exit, preventing deadlocks
 * from early returns or exceptions. Zero overhead abstraction.
 */

/**
 * @brief RAII wrapper for mutex locks
 * 
 * Automatically locks mutex on construction and unlocks on destruction.
 * Prevents common deadlock scenarios from forgotten unlocks.
 * 
 * @tparam MutexType Type of mutex to lock (e.g., Threads::Mutex)
 * 
 * Example usage:
 * @code
 * Threads::Mutex my_mutex;
 * 
 * void critical_section() {
 *     scoped_lock lock(my_mutex);  // Locks here
 *     // ... critical work ...
 * }  // Automatically unlocks here, even if early return
 * @endcode
 */
template<typename MutexType>
class scoped_lock {
public:
    /**
     * @brief Construct and lock the mutex
     * @param mutex Reference to mutex to lock
     */
    explicit scoped_lock(MutexType& mutex) : mutex_(mutex) { 
        mutex_.lock(); 
    }
    
    /**
     * @brief Destruct and unlock the mutex
     */
    ~scoped_lock() { 
        mutex_.unlock(); 
    }
    
    // Delete copy operations to prevent double-unlock
    scoped_lock(const scoped_lock&) = delete;
    scoped_lock& operator=(const scoped_lock&) = delete;
    
    // Delete move operations (not needed for RAII guard)
    scoped_lock(scoped_lock&&) = delete;
    scoped_lock& operator=(scoped_lock&&) = delete;

private:
    MutexType& mutex_;
};
