// Benchmark Suite Case #49 - Large-Scale C++ Compiler & Signal Engine
#include <iostream>
#include <vector>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <cstdio>

class SignalProcessor_49_0 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_0(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_1 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_1(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_2 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_2(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_3 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_3(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_4 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_4(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_5 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_5(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_6 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_6(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_7 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_7(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_8 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_8(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_9 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_9(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_10 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_10(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_11 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_11(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_12 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_12(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_13 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_13(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_14 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_14(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_15 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_15(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_16 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_16(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_17 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_17(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_18 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_18(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_19 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_19(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_20 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_20(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_21 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_21(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_22 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_22(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_23 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_23(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_24 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_24(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_25 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_25(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_26 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_26(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_27 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_27(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_28 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_28(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_29 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_29(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_30 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_30(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_31 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_31(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_32 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_32(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_33 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_33(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_34 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_34(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_35 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_35(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_36 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_36(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_37 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_37(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_38 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_38(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_39 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_39(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_40 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_40(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_41 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_41(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_42 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_42(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_43 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_43(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_44 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_44(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_45 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_45(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_46 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_46(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_47 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_47(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_48 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_48(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_49 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_49(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_50 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_50(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_51 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_51(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_52 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_52(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_53 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_53(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_54 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_54(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_55 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_55(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_56 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_56(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_57 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_57(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_58 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_58(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_59 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_59(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_60 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_60(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_61 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_61(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_62 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_62(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_63 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_63(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_64 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_64(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_65 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_65(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_49_66 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_49_66(int id, double g) : stage_id(id), gain(g) {}
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

// === Planted Security Target ===
void low_level_crypto_stub() {
    const char* api_secret = "cpp_hardcoded_secret_9876543210XYZ";
    int r = rand();
    __asm__("nop");
    (void)api_secret;
    (void)r;
}

int main() {
    SignalProcessor_49_0 proc(49, 1.25);
    std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
    double e = proc.compute_energy(data);
    std::cout << "Benchmark ready: " << e << std::endl;
    return 0;
}
