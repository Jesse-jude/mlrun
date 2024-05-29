# Copyright 2024 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd

import mlrun.common.schemas.model_monitoring as mm_schemas


class TSDBConnector(ABC):
    type: str = ""

    def __init__(self, project: str):
        """
        Initialize a new TSDB connector. The connector is used to interact with the TSDB and store monitoring data.
        At the moment we have 3 different types of monitoring data:
        - real time performance metrics: real time performance metrics that are being calculated by the model
        monitoring stream pod.
        Among these metrics are the base metrics (average latency and predictions over time), endpoint features
        (data samples), and custom metrics (user-defined metrics).
        - app_results: a detailed results that include status, kind, extra data, etc. These results are being calculated
        through the monitoring applications and stored in the TSDB using the model monitoring writer.
        - metrics: a basic key value that represents a numeric metric. Similar to the app_results, these metrics
        are being calculated through the monitoring applications and stored in the TSDB using the model monitoring
        writer.

        :param project: the name of the project.

        """
        self.project = project

    def apply_monitoring_stream_steps(self, graph):
        """
        Apply TSDB steps on the provided monitoring graph. Throughout these steps, the graph stores live data of
        different key metric dictionaries. This data is being used by the monitoring dashboards in
        grafana.
        There are 3 different key metric dictionaries that are being generated throughout these steps:
        - base_metrics (average latency and predictions over time)
        - endpoint_features (Prediction and feature names and values)
        - custom_metrics (user-defined metrics)
        """
        pass

    def write_application_event(
        self,
        event: dict,
        kind: mm_schemas.WriterEventKind = mm_schemas.WriterEventKind.RESULT,
    ) -> None:
        """
        Write a single application or metric to TSDB.

        :raise mlrun.errors.MLRunRuntimeError: If an error occurred while writing the event.
        """

    def delete_tsdb_resources(self):
        """
        Delete all project resources in the TSDB connector, such as model endpoints data and drift results.
        """

        pass

    def get_model_endpoint_real_time_metrics(
        self,
        endpoint_id: str,
        metrics: list[str],
        start: str,
        end: str,
    ) -> dict[str, list[tuple[str, float]]]:
        """
        Getting real time metrics from the TSDB. There are pre-defined metrics for model endpoints such as
        `predictions_per_second` and `latency_avg_5m` but also custom metrics defined by the user. Note that these
        metrics are being calculated by the model monitoring stream pod.
        :param endpoint_id:      The unique id of the model endpoint.
        :param metrics:          A list of real-time metrics to return for the model endpoint.
        :param start:            The start time of the metrics. Can be represented by a string containing an  RFC 3339
                                 time, a  Unix timestamp in milliseconds, a relative time (`'now'` or
                                 `'now-[0-9]+[mhd]'`, where `m` = minutes, `h` = hours, `'d'` = days, and `'s'`
                                 = seconds), or 0 for the earliest time.
        :param end:              The end time of the metrics. Can be represented by a string containing an  RFC 3339
                                 time, a  Unix timestamp in milliseconds, a relative time (`'now'` or
                                 `'now-[0-9]+[mhd]'`, where `m` = minutes, `h` = hours, `'d'` = days, and `'s'`
                                 = seconds), or 0 for the earliest time.
        :return: A dictionary of metrics in which the key is a metric name and the value is a list of tuples that
                 includes timestamps and the values.
        """
        pass

    @abstractmethod
    def get_records(
        self,
        table: str,
        start: str,
        end: str,
        columns: typing.Optional[list[str]] = None,
        filter_query: str = "",
    ) -> pd.DataFrame:
        """
        Getting records from TSDB data collection.
        :param table:            Table name, e.g. 'metrics', 'app_results'.
        :param start:            The start time of the metrics.
                                 If using V3IO, can be represented by a string containing an RFC 3339 time, a  Unix
                                 timestamp in milliseconds, a relative time (`'now'` or `'now-[0-9]+[mhd]'`, where
                                 `m` = minutes, `h` = hours, `'d'` = days, and `'s'` = seconds), or 0 for the earliest
                                 time.
                                 If using TDEngine, can be represented by datetime.
        :param end:              The end time of the metrics.
                                 If using V3IO, can be represented by a string containing an RFC 3339 time, a  Unix
                                 timestamp in milliseconds, a relative time (`'now'` or `'now-[0-9]+[mhd]'`, where
                                 `m` = minutes, `h` = hours, `'d'` = days, and `'s'` = seconds), or 0 for the earliest
                                 time.
                                 If using TDEngine, can be represented by datetime.
        :param columns:          Columns to include in the result.
        :param filter_query:     Optional filter expression as a string. The filter structure depends on the TSDB
                                 connector type.


        :return: DataFrame with the provided attributes from the data collection.
        :raise:  MLRunNotFoundError if the provided table wasn't found.
        """

    def create_tables(self) -> None:
        """
        Create the TSDB tables using the TSDB connector. At the moment we support 3 types of tables:
        - app_results: a detailed result that includes status, kind, extra data, etc.
        - metrics: a basic key value that represents a numeric metric.
        - predictions: latency of each prediction.
        """

    @abstractmethod
    def read_metrics_data(
        self,
        *,
        endpoint_id: str,
        start: datetime,
        end: datetime,
        metrics: list[mm_schemas.ModelEndpointMonitoringMetric],
        type: typing.Literal["metrics", "results"],
    ) -> typing.Union[
        list[
            typing.Union[
                mm_schemas.ModelEndpointMonitoringResultValues,
                mm_schemas.ModelEndpointMonitoringMetricNoData,
            ],
        ],
        list[
            typing.Union[
                mm_schemas.ModelEndpointMonitoringMetricValues,
                mm_schemas.ModelEndpointMonitoringMetricNoData,
            ],
        ],
    ]:
        """
        Read metrics OR results from the TSDB and return as a list.

        :param endpoint_id: The model endpoint identifier.
        :param start:       The start time of the query.
        :param end:         The end time of the query.
        :param metrics:     The list of metrics to get the values for.
        :param type:        "metrics" or "results" - the type of each item in metrics.
        :return:            A list of result values or a list of metric values.
        """

    @abstractmethod
    def read_predictions(
        self,
        *,
        endpoint_id: str,
        start: datetime,
        end: datetime,
        aggregation_window: typing.Optional[str] = None,
    ) -> typing.Union[
        mm_schemas.ModelEndpointMonitoringMetricValues,
        mm_schemas.ModelEndpointMonitoringMetricNoData,
    ]:
        """
        Read the "invocations" metric for the provided model endpoint in the given time range,
        and return the metric values if any, otherwise signify with the "no data" object.

        :param endpoint_id:        The model endpoint identifier.
        :param start:              The start time of the query.
        :param end:                The end time of the query.
        :param aggregation_window: On what time window length should the invocations be aggregated.
        :return:                   Metric values object or no data object.
        """

    @abstractmethod
    def read_prediction_metric_for_endpoint_if_exists(
        self, endpoint_id: str
    ) -> typing.Optional[mm_schemas.ModelEndpointMonitoringMetric]:
        """
        Read the "invocations" metric for the provided model endpoint, and return the metric object
        if it exists.

        :param endpoint_id: The model endpoint identifier.
        :return:            `None` if the invocations metric does not exist, otherwise return the
                            corresponding metric object.
        """