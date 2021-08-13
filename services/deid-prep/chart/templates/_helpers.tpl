{{/*
Expand the name of the chart.
*/}}
{{- define "deid-prep.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "deid-prep.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "deid-prep.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "deid-prep.labels" -}}
helm.sh/chart: {{ include "deid-prep.chart" . }}
{{ include "deid-prep.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "deid-prep.selectorLabels" -}}
app.kubernetes.io/name: {{ include "deid-prep.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "deid-prep.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "deid-prep.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the FHIR server to use
*/}}
{{- define "deid-prep.fhir.url" -}}
{{- if .Values.fhir.url }}
{{- .Values.fhir.url }}
{{- else }}
{{- printf "\"http://%s-fhir-deid/fhir-server/api/v4\"" .Release.Name }}
{{- end }}
{{- end }}

{{/*
Create the name of the De-Id server to use
*/}}
{{- define "deid-prep.deid.url" -}}
{{- if .Values.deid.url }}
{{- .Values.deid.url }}
{{- else }}
{{- printf "\"http://%s-deid:8080/api/v1\"" .Release.Name }}
{{- end }}
{{- end }}
