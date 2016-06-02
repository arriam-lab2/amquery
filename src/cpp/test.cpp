#include <string>
#include <iostream>
#include <assert.h>
#include <map>
#include <vector>

#include <cache.h>

struct Foo
{
    int a;

    bool operator==(const Foo& other)
    {
        return a == other.a;
    }
};

using namespace collections;

void test_create()
{
    lru_cache<std::string, Foo> x;
    assert(x.empty());
    assert(x.size() == 0);
    assert(x.max_size() == 50);

    lru_cache<std::string, Foo> y(10);
    assert(y.max_size() == 10);
}

void test_simple_insert()
{
    lru_cache<std::string, Foo> x;

    Foo f { 1 };
    auto result = x.insert(std::make_pair("f", f));
    assert(result.second == true);
    assert(result.first->second == f);

    result = x.insert(std::make_pair("f", f));
    assert(result.second == false);
    assert(result.first->second == f);

    Foo g { 10 };
    result = x.insert(std::make_pair("g", g));
    assert(result.second == true);
    assert(result.first->second == g);
}

void test_lru_insert()
{
    const int max_count = 20;
    lru_cache<std::string, Foo> cache(max_count);

    for (size_t i = 0; i < max_count; ++i)
    {
        Foo f { (int)i };
        std::string key = "f";
        key += std::to_string(i);

        auto result = cache.insert(std::make_pair(key, f));
        assert(result.second == true);
        assert(result.first->second == f);
        assert(cache.size() == i + 1);
        assert(cache[key] == f);
    }

    std::map<std::string, Foo> objects;
    for (size_t i = max_count; i < 2 * max_count; ++i)
    {
        Foo f { (int)i };
        std::string key = "f";
        key += std::to_string(i);

        auto result = cache.insert(std::make_pair(key, f));
        assert(result.second == true);
        assert(result.first->second == f);
        assert(cache.size() == max_count);
        assert(cache[key] == f);

        objects[key] = f;
    }

    for (auto kv : objects)
    {
        assert(cache[kv.first] == kv.second);
    }
}

void test_lru_update()
{
    const int max_count = 5;
    lru_cache<std::string, Foo> cache(max_count);

    for (size_t i = 0; i < max_count; ++i)
    {
        auto it = cache.insert(std::make_pair(std::to_string(i),
                                              Foo { (int)i } ));
        assert(it.second == true);
        assert(it.first->second == Foo { (int) i});
    }
    cache["0"];
    cache["1"];
    cache["2"];

    cache.insert(std::make_pair("42",
                                Foo { 42 }));

    std::vector<std::string> keys = { "0", "1", "2", "4", "42" };
    for (auto key: keys)
    {
        (void)cache[key];
    }
    assert(cache.size() == 5);
    assert(cache.max_size() == 5);
}

int main()
{
    test_create();
    test_simple_insert();
    test_lru_insert();
    test_lru_update();
    return 0;
}
