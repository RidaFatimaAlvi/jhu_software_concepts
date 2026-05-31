from urllib import parse, robotparser

agent = "rida"
url = "https://www.thegradcafe.com/"

parser = robotparser.RobotFileParser()
parser.set_url(parse.urljoin(url, "robots.txt"))
parser.read()

print(parser.can_fetch(agent, url))