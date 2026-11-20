// Benchmark Suite Case #46 - Large-Scale C++ Compiler & Signal Engine
#include <iostream>
#include <vector>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <cstdio>

class SignalProcessor_46_0 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_0(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_1 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_1(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_2 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_2(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_3 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_3(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_4 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_4(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_5 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_5(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_6 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_6(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_7 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_7(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_8 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_8(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_9 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_9(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_10 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_10(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_11 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_11(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_12 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_12(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_13 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_13(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_14 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_14(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_15 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_15(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_16 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_16(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_17 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_17(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_18 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_18(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_19 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_19(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_20 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_20(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_21 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_21(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_22 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_22(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_23 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_23(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_24 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_24(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_25 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_25(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_26 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_26(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_27 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_27(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_28 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_28(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_29 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_29(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_30 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_30(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_31 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_31(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_32 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_32(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_33 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_33(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_34 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_34(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_35 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_35(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_36 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_36(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_37 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_37(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_38 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_38(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_39 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_39(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_40 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_40(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_41 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_41(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_42 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_42(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_43 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_43(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_44 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_44(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_45 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_45(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_46 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_46(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_47 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_47(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_48 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_48(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_49 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_49(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_50 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_50(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_51 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_51(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_52 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_52(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_53 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_53(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_54 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_54(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_55 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_55(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_56 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_56(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_57 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_57(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_58 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_58(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_59 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_59(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_60 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_60(int id, double g) : stage_id(id), gain(g) {}
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

class SignalProcessor_46_61 {
private:
    int stage_id;
    double gain;
public:
    SignalProcessor_46_61(int id, double g) : stage_id(id), gain(g) {}
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
void legacy_shell_bridge(const char* input) {
    char buf[64];
    strcpy(buf, input);
    std::system(buf);
}

int main() {
    SignalProcessor_46_0 proc(46, 1.25);
    std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
    double e = proc.compute_energy(data);
    std::cout << "Benchmark ready: " << e << std::endl;
    return 0;
}
