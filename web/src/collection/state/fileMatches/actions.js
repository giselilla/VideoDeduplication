/**
 * "Update matches params" action type.
 * @type {string}
 */
export const ACTION_UPDATE_FILE_MATCHES_PARAMS =
  "coll.UPDATE_FILE_MATCHES_PARAMS";

/**
 * Create new "Update matches params" action.
 */
export function updateFileMatchesParams(params) {
  return { params, type: ACTION_UPDATE_FILE_MATCHES_PARAMS };
}

/**
 * "Fetch the next matches slice" action type.
 * @type {string}
 */
export const ACTION_FETCH_FILE_MATCHES_SLICE = "coll.FETCH_FILE_MATCHES_SLICE";

/**
 * Create new "Fetch the next matches slice" action.
 * @return {{type: string}}
 */
export function fetchFileMatchesSlice() {
  return { type: ACTION_FETCH_FILE_MATCHES_SLICE };
}

/**
 * "Success of matches slice fetching" action type.
 * @type {string}
 */
export const ACTION_FETCH_FILE_MATCHES_SLICE_SUCCESS =
  "coll.FETCH_FILE_MATCHES_SLICE_SUCCESS";

/**
 * Create new "Success of matches slice fetching" action.
 */
export function fetchFileMatchesSliceSuccess({ matches, total }) {
  return { matches, total, type: ACTION_FETCH_FILE_MATCHES_SLICE_SUCCESS };
}

/**
 * "Failure of matches slice fetching" action type.
 * @type {string}
 */
export const ACTION_FETCH_FILE_MATCHES_SLICE_FAILURE =
  "coll.FETCH_FILE_MATCHES_SLICE_FAILURE";

/**
 * Create new "Failure of matches slice fetching" action.
 * @param error
 * @return {{error: *, type: string}}
 */
export function fetchFileMatchesSliceFailure(error) {
  return { error, type: ACTION_FETCH_FILE_MATCHES_SLICE_FAILURE };
}
