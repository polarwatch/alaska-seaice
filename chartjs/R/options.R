#' Edit default options
#'
#' Allows editing of the chart options.
#'
#' @param chartjs a \code{\link{chartjs}} object
#' @param ... named arguments, see Details
#'
#' @details The allowed values in \code{...} can be found in the
#' \href{http://www.chartjs.org/docs/#getting-started-global-chart-configuration}{Chart.js documentation}
#' under \code{Charts.default.global}. You can also use this function to edit the \code{animation} and \code{elements}
#' options by passing them as a list, or to edit the chart-specific options.
#' To edit tooltips, legends or titles, use the corresponding functions.
#' @export
#' @name options
cjsOptions <- function(chartjs, ...){
  ldots <- list(...)
  chartjs$x$options <- mergeLists(chartjs$x$options, ldots)
  chartjs
}

#' Description of the cjsInteraction function.
#'
#' @param chartjs a \code{\link{chartjs}} object
#' @param ... named arguments, see Details
#'
#' @export


cjsInteraction <- function(chartjs, ...){
  ldots <- list(...)
  chartjs$x$options$interaction$axis = "index"
  chartjs$x$options$interaction$mode = "nearest"
  chartjs$x$options$interaction$intersect = FALSE
  chartjs
}

