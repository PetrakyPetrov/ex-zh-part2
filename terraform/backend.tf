terraform {
  backend "gcs" {
    credentials = "ppetrov-internal-402521-b03011e54c0e.json"
    bucket      = "ex-zh-part2-function"
    prefix      = "function"
  }
}