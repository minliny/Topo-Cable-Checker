// api/services.ts
// Page-level service layer
// Uses apiClient from provider (default: mock, switchable to real)

import { apiClient } from './provider';

// ── Baseline Services ───────────────────────────────────────────────────────
export const getBaselineList = async () => {
  const result = await apiClient.getBaselineList();
  return result.baselines;
};

export const getBaselineDetail = async (baselineId: string) => {
  const result = await apiClient.getBaselineDetail(baselineId);
  return result;
};

export const updateBaseline = async (baselineId: string, request: any) => {
  return await apiClient.updateBaseline(baselineId, request);
};

export const getBaselineProfileMapEntry = async (baselineId: string) => {
  const result = await apiClient.getBaselineProfileMapEntry(baselineId);
  return result;
};

export const getBaselineVersionSnapshot = async (baselineId: string) => {
  const result = await apiClient.getBaselineVersionSnapshot(baselineId);
  return result;
};

// ── Profile/Scope Services ───────────────────────────────────────────────────
export const getParameterProfileList = async () => {
  const result = await apiClient.getParameterProfileList();
  return result.profiles;
};

export const getThresholdProfileList = async () => {
  const result = await apiClient.getThresholdProfileList();
  return result.profiles;
};

export const getScopeSelectorList = async () => {
  const result = await apiClient.getScopeSelectorList();
  return result.selectors;
};

export const getRuleSetList = async () => {
  const result = await apiClient.getRuleSetList();
  return result.rulesets;
};

// ── Rule Editor Services ─────────────────────────────────────────────────────
export const getRuleDefinitions = async () => {
  const result = await apiClient.getRuleDefinitions();
  return result.rules;
};

export const updateRuleOverride = async (request: any) => {
  return await apiClient.updateRuleOverride(request);
};

// ── Version Management Services ───────────────────────────────────────────────
export const getVersionList = async (baselineId: string) => {
  const result = await apiClient.getVersionList(baselineId);
  return result.versions;
};

export const getVersionSnapshot = async (versionId: string) => {
  const result = await apiClient.getVersionSnapshot(versionId);
  return result.snapshot;
};

export const getVersionDiff = async (fromVersion: string, toVersion: string) => {
  const result = await apiClient.getVersionDiff(fromVersion, toVersion);
  return result.diff;
};

export const createVersion = async (baselineId: string, request: any) => {
  const result = await apiClient.createVersion(baselineId, request);
  return result;
};

export const publishVersion = async (request: any) => {
  return await apiClient.publishVersion(request);
};

// ── Execution Config Services ─────────────────────────────────────────────────
export const getDataSourceList = async () => {
  const result = await apiClient.getDataSourceList();
  return result.data_sources;
};

export const getScopeList = async () => {
  const result = await apiClient.getScopeList();
  return result.scopes;
};

export const getRecognitionStatus = async () => {
  const result = await apiClient.getRecognitionStatus();
  return result;
};

export const startRecognition = async (request: any) => {
  const result = await apiClient.startRecognition(request);
  return result;
};

export const confirmRecognition = async (request: any) => {
  return await apiClient.confirmRecognition(request);
};

export const startCheck = async (request: any) => {
  const result = await apiClient.startCheck(request);
  return result;
};

// ── Run History Services ──────────────────────────────────────────────────────
export const getRunHistory = async () => {
  const result = await apiClient.getRunHistory();
  return result.runs;
};

export const getRunDetail = async (runId: string) => {
  const result = await apiClient.getRunDetail(runId);
  return result;
};

// ── Analysis Workbench Services ───────────────────────────────────────────────
export const getCheckResultBundle = async (bundleId: string) => {
  const result = await apiClient.getCheckResultBundle(bundleId);
  return result.bundle;
};

export const getIssueDetail = async (issueId: string) => {
  const result = await apiClient.getIssueDetail(issueId);
  return result.issue;
};

// ── Diff Compare Services ─────────────────────────────────────────────────────
export const getRecheckDiff = async (baseRunId: string, targetRunId: string) => {
  const result = await apiClient.getRecheckDiff(baseRunId, targetRunId);
  return result.diff;
};
