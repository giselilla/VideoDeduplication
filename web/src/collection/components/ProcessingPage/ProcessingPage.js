import React, { useCallback } from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import ProcessingPageHeader from "./ProcessingPageHeader";
import { useHistory } from "react-router-dom";
import { routes } from "../../../routing/routes";
import FileSelector from "./FileSelector";
import TaskSidebar from "./TaskSidebar";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.dimensions.content.padding,
    paddingTop: theme.dimensions.content.padding * 3,
    minWidth: theme.dimensions.collectionPage.width,
  },
  content: {
    display: "flex",
    alignItems: "stretch",
  },
  selector: {
    flexGrow: 1,
  },
  tasks: {
    marginLeft: theme.spacing(4),
  },
}));

function ProcessingPage(props) {
  const { className, ...other } = props;
  const classes = useStyles();
  const history = useHistory();

  const handleClose = useCallback(
    () => history.push(routes.collection.fingerprints, { keepFilters: true }),
    []
  );

  return (
    <div className={clsx(classes.root, className)} {...other}>
      <ProcessingPageHeader onClose={handleClose} />
      <div className={classes.content}>
        <FileSelector className={classes.selector} />
        <TaskSidebar className={classes.tasks} />
      </div>
    </div>
  );
}

ProcessingPage.propTypes = {
  className: PropTypes.string,
};

export default ProcessingPage;