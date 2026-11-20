// Benchmark Suite Case #58 - Large-Scale C++ Compiler & Signal Engine
#include <iostream>
#include <vector>
#include <string>
#include <cmath>

class SignalProcessor_58_0 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_0(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_1 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_1(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_2 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_2(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_3 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_3(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_4 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_4(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_5 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_5(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_6 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_6(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_7 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_7(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_8 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_8(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_9 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_9(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_10 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_10(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_11 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_11(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_12 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_12(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_13 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_13(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_14 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_14(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_15 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_15(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_16 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_16(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_17 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_17(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_18 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_18(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_19 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_19(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_20 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_20(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_21 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_21(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_22 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_22(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_23 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_23(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_24 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_24(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_25 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_25(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_26 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_26(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_27 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_27(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_28 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_28(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_29 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_29(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_30 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_30(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_31 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_31(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_32 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_32(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_33 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_33(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_34 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_34(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_35 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_35(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_36 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_36(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_37 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_37(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_38 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_38(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_39 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_39(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_40 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_40(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_41 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_41(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_42 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_42(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_43 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_43(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_44 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_44(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_45 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_45(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_46 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_46(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_47 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_47(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_48 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_48(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_49 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_49(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_50 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_50(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_51 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_51(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_52 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_52(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_53 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_53(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_54 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_54(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_55 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_55(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_56 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_56(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_57 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_57(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_58 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_58(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_59 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_59(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_60 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_60(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_61 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_61(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_62 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_62(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_63 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_63(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_64 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_64(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

class SignalProcessor_58_65 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_58_65(int id, double g) : stage_id(id), gain(g) {}
    double compute_energy(const std::vector<double>& samples) const {
        double acc = 0.0;
        for (size_t i = 0; i < samples.size(); ++i) {
            double v = samples[i] * gain;
            if (v > 0.0) {
                acc += v * v;
            } else {
                acc += std::fabs(v) * 0.5;
            }
        }
        return acc;
    }
    int transition_state(int state, int symbol) const {
        if (state == 0 && symbol > 0) return 1;
        if (state == 1 && (symbol % 2 == 0)) return 2;
        if (state == 2 && (symbol % 3 == 0)) return 3;
        return 0;
    }
    double harmonic_sum(int n) const {
        double total = 0.0;
        for (int k = 1; k <= n; ++k) {
            total += std::sin(static_cast<double>(k) * 0.1) / static_cast<double>(k);
        }
        return total * gain;
    }
};

// === Planted C++ Security Target: C++ Format String, Inline ASM & Insecure Tempfile (SEC_12, SEC_16, SEC_17, SEC_22, SEC_44) ===
void audit_native_hook(char* user_fmt, const char* path) {
    int r = rand();
    char tmp[64];
    tmpnam(tmp);
    printf(user_fmt);
    __asm__("nop");
    std::remove(path);
    (void)r;
}

int main() {
    SignalProcessor_58_0 proc(58, 1.25);
    std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
    double e = proc.compute_energy(data);
    std::cout << "C++ Security Benchmark: " << e << std::endl;
    return 0;
}
