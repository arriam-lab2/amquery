#pragma once

#include <vector>
#include <queue>
#include <memory>
#include <functional>
#include <stdexcept>
//#include <condition_variable>


#define BOOST_THREAD_PROVIDES_FUTURE

#include <boost/thread/mutex.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/future.hpp>
#include <boost/thread/condition_variable.hpp>

namespace concurrent
{
    // Adapted version of
    // https://github.com/progschj/ThreadPool
    class thread_pool
    {
    public:
        thread_pool(size_t size)
            : _stop(false)
        {
            for (size_t i = 0; i < size; ++i)
                _pool.emplace_back(
                    [this]
                    {
                        while (is_alive())
                        {
                            std::function<void()> task;

                            {
                                boost::unique_lock<boost::mutex> lock(_queue_mutex);
                                _condition.wait(lock,
                                    [this] {
                                        return _stop || !_tasks.empty();
                                    }
                                );

                                if (!is_alive())
                                {
                                    return;
                                }

                                task = std::move(_tasks.front());
                                _tasks.pop();
                            }

                            task();
                        }
                    }
                );
        }

        thread_pool(const thread_pool&) = delete;
        thread_pool(thread_pool&&) = delete;
        thread_pool& operator=(const thread_pool&) = delete;
        thread_pool operator=(thread_pool&&) = delete;

        ~thread_pool()
        {
            {
                boost::unique_lock<boost::mutex> lock(_queue_mutex);
                _stop = true;
            }

            _condition.notify_all();

            for (boost::thread& worker: _pool)
            {
                worker.join();
            }
        }

        template <class Function,
                  class... Args,
                  class return_type = typename std::result_of<Function(Args...)>::type>
        auto submit(Function&& function, Args&&... args)
            -> boost::future<return_type>
        {
            auto binded = std::bind(std::forward<Function>(function),
                                    std::forward<Args>(args)...);

            using task_type = boost::packaged_task<return_type>;
            std::shared_ptr<task_type> task = std::make_shared<task_type>(binded);
            boost::future<return_type> future = task->get_future();
            {
                boost::unique_lock<boost::mutex> lock(_queue_mutex);

                // don't allow enqueueing after stopping the pool
                if (_stop)
                {
                    throw std::runtime_error("enqueue on stopped ThreadPool");
                }

                _tasks.emplace([task] { (*task)(); });
            }

            _condition.notify_one();
            return future;
        }

    private:
        bool is_alive()
        {
            return !(_stop && _tasks.empty());
        }

    private:
        std::vector<boost::thread> _pool;
        std::queue<std::function<void()>> _tasks;

        boost::mutex _queue_mutex;
        boost::condition_variable _condition;
        bool _stop;
    };

}
