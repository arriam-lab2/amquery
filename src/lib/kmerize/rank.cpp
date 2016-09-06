#include <cstdint>
#include <cstddef>


uint64_t ipow(uint64_t base, uint64_t exp)
{
    uint64_t result = 1;
    while (exp)
    {
        if (exp & 1)
            result *= base;
        exp >>= 1;
        base *= base;
    }

    return result;
}

void kmer_ranks(const uint8_t* in, uint64_t* out, const size_t n, const size_t k)
{
    const uint64_t m = 4;

    out[0] = 0;
    for (size_t i = 0; i < k; ++i)
        out[0] += in[i] * ipow(m, k-i-1);

    for (size_t i = 1; i < n - k + 1; ++i)
        out[i] = m * (out[i-1] - in[i-1] * ipow(m, k - 1)) + in[i+k-1];
}

extern "C" {
    void count_kmer_ranks(const uint8_t* in, uint64_t* out, const size_t n, const uint8_t k)
    {
        kmer_ranks(in, out, n, k);
    }
}
