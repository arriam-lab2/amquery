#include <cstdint>
#include <cstddef>
#include <vector>
#include <functional>
#include <algorithm>
#include <cmath>
#include <numeric>

#include <iostream>
#include <fstream>

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

    void apply(const std::function<T(T)>& f)
    {
        std::transform(data.begin(), data.end(),
                       data.begin(), f);
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

sparse_array positional_map(sparse_array&& x, sparse_array&& y,
                            transformer func, num_t default_value = 0)
{
    std::vector<num_t> values(x.size());
    size_t j = 0;
    for (size_t i = 0; i < x.size(); ++i)
    {
        while (x.idx[i] > y.idx[j] && j < y.size())
            ++j;

        if (x.idx[i] == y.idx[j])
        {
            values[i] = func(x.data[i], y.data[j]);
            ++j;
        }
        else
            values[i] = default_value;
    }
    return sparse_array(std::move(x.idx), std::move(values));
}


sparse_array positional_merge(sparse_array&& x, sparse_array&& y,
                              transformer func, num_t default_value = 0)
{
    sparse_array result;
    result.reserve(std::max(x.size(), y.size()));

    int i = 0, j = 0;
    size_t xsize = x.size(), ysize = y.size();
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
        }
        else if (j < 0 || (i >= 0 && x.idx[i] < y.idx[j]))
        {
            temp = func(x.data[i], default_value);
            index = x.idx[i];

            i = i < xsize - 1 ? i + 1 : -1;
        }
        else
        {
            temp = func(default_value, y.data[j]);
            index = y.idx[j];
            j = j < ysize - 1? j + 1 : -1;
        }
        result.push_back(index, temp);

    }
    return result;

}

num_t sum(num_t a, num_t b)
{
    return a + b;
}

num_t mul2(num_t a)
{
    return a * 2;
}

num_t divide(num_t a, num_t b)
{
    return b != 0 ? a / b : 0;
}

num_t mul(num_t a, num_t b)
{
    return a * b;
}

double _jsd(const index_t* x_pos, const num_t* x_val,
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

    sparse_array z = positional_merge(std::move(x), std::move(y), sum);

    sparse_array d1 = x.copy();
    d1.apply(mul2);
    d1 = positional_map(std::move(d1), std::move(z), divide);
    d1.apply(log2);
    d1 = positional_map(std::move(d1), std::move(x), mul);

    sparse_array d2 = y.copy();
    d2.apply(mul2);
    d2 = positional_map(std::move(d2), std::move(z), divide);
    d2.apply(log2);
    d2 = positional_map(std::move(d2), std::move(y), mul);

    d1 = positional_merge(std::move(d1), std::move(d2), sum);

    num_t result = 0;
    for (auto v : d1.data)
        result += v;

    return sqrt(result / 2);
}

extern "C" {
    double jsd(const index_t* x_pos, const num_t* x_val,
               const size_t x_len,
               const index_t* y_pos, const num_t* y_val,
               const size_t y_len)
    {
        return _jsd(x_pos, x_val, x_len, y_pos, y_val, y_len);
    }
}


int main()
{
    std::vector<index_t> xpos = {8, 15, 17, 32, 57, 60, 63, 72, 97};
    std::vector<num_t> xval = {0.198113, 0.115566, 0.0636792, 0.0306604,
         0.148585, 0.00943396, 0.117925, 0.132075, 0.183962};

    std::vector<index_t> ypos = {0, 13, 29, 34, 57, 75, 89, 92, 97, 98};
    std::vector<num_t> yval = {0.10992, 0.0107239, 0.0080429, 0.0107239,
         0.225201, 0.187668, 0.00536193, 0.131367, 0.235925, 0.075067 };

    std::cout << jsd(&xpos[0], &xval[0], xpos.size(),
                     &ypos[0], &yval[0], ypos.size()) << std::endl;

}
