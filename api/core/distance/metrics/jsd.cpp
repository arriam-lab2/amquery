#include <cstdint>
#include <cstddef>
#include <vector>
#include <functional>
#include <algorithm>
#include <cmath>
#include <numeric>

typedef double num_t;
typedef uint64_t index_t;
typedef std::function<num_t(num_t, num_t)> transformer;

template <typename IndexType, typename T>
struct sparse_array_t
{
    std::vector<IndexType> idx;
    std::vector<T> data;

    typedef std::vector<IndexType> idx_t;
    typedef std::vector<T> data_t;

    sparse_array_t(size_t size=0)
        : idx(std::vector<IndexType>(size))
        , data(std::vector<T>(size))
    {}

    sparse_array_t(const sparse_array_t&) = delete;

    sparse_array_t(idx_t&& other_idx, data_t&& other_data)
        : idx(std::move(other_idx))
        , data(std::move(other_data))
    {}

    sparse_array_t(sparse_array_t&& other)
        : sparse_array_t(std::move(other.idx),
                         std::move(other.data))
    {}

    // WARNING: dangerous
    sparse_array_t& operator=(sparse_array_t&& other)
    {
        std::swap(idx, other.idx);
        std::swap(data, other.data);
        return *this;
    }

    sparse_array_t copy() const
    {
        sparse_array_t result(size());
        std::copy(idx.begin(), idx.end(), result.idx.begin());
        std::copy(data.begin(), data.end(), result.data.begin());
        return result;
    }

    sparse_array_t&& apply(const std::function<T(T)>& f)
    {
        std::transform(data.begin(), data.end(),
                       data.begin(), f);
        return std::move(*this);
    }

    void push_back(const IndexType& i, const T& value)
    {
        idx.push_back(i);
        data.push_back(value);
    }

    size_t size() const
    {
        return idx.size();
    }

    void reserve(size_t size)
    {
        idx.reserve(size);
        data.reserve(size);
    }
};

typedef sparse_array_t<index_t, num_t> sparse_array;

sparse_array skipping_merge(sparse_array&& x, sparse_array&& y,
                            transformer func, num_t default_value = 0)
{
    sparse_array result;
    result.reserve(std::max(x.size(), y.size()));

    long i = 0, j = 0;
    long xsize = x.size(), ysize = y.size();
    while (i >= 0 || j >= 0)
    {
        num_t temp = 0;
        index_t index = -1;

        if (i >= 0 && j >=0 && x.idx[i] == y.idx[j])
        {
            temp = func(x.data[i], y.data[j]);
            index = x.idx[i];
            i = i < xsize - 1 ? i + 1 : -1;
            j = j < ysize - 1 ? j + 1 : -1;

            result.push_back(index, temp);
        }
        else if (j < 0 || (i >= 0 && x.idx[i] < y.idx[j]))
        {
            i = i < xsize - 1 ? i + 1 : -1;
        }
        else
        {
            j = j < ysize - 1? j + 1 : -1;
        }
    }
    return result;

}

num_t h(num_t x)
{
    return -x * log2(x);
}

num_t kernel(num_t a, num_t b)
{
    return h(a) + h(b) - h(a + b);
}


double _fast_jsd(const index_t* x_pos, const num_t* x_val,
                 const size_t x_len,
                 const index_t* y_pos, const num_t* y_val,
                 const size_t y_len)
{
    sparse_array x(
        std::vector<index_t>(x_pos, x_pos + x_len),
        std::vector<num_t>(x_val, x_val + x_len)
    );

    sparse_array y(
        std::vector<index_t>(y_pos, y_pos + y_len),
        std::vector<num_t>(y_val, y_val + y_len)
    );

    sparse_array f = skipping_merge(std::move(x), std::move(y), kernel);
    double result = 0;
    for (auto v : f.data)
    {
        result += v;
    }
    return sqrt(1.0 - 0.5 * result);
}

extern "C" {
    double jsd(const index_t* x_pos, const num_t* x_val,
               const size_t x_len,
               const index_t* y_pos, const num_t* y_val,
               const size_t y_len)
    {
        return _fast_jsd(x_pos, x_val, x_len, y_pos, y_val, y_len);
    }
}