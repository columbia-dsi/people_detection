import pickle
from tornado import gen, httpserver, ioloop, log, web
import sys

PREDICTION_DIR_PATH = '/Users/harish/IdeaProjects/datascience_certification/data_analytics_pipeline/project/prediction'


class MainHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        prediction_json = pickle.load(
            open('{}/pred.pickle'.format(PREDICTION_DIR_PATH), 'rb'))
        self.write(prediction_json)


def make_app():
    return web.Application([
        (r"/", MainHandler)
    ],
        debug=False)


def main():
    app = make_app()
    # start server
    server = httpserver.HTTPServer(app)
    server.listen(8080)

    print('starting ioloop')
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PREDICTION_DIR_PATH = int(sys.argv[1])

    main()

# To dos:
# Dockerize the application
# Improve the consumer - just return the last unconsumed message in a non-blocking manner
