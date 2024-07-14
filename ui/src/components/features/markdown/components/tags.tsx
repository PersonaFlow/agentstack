import { ComponentPropsWithoutRef } from "react";
import type {
  //   Component,
  ExtraProps,
} from "hast-util-to-jsx-runtime";

export const P = ({ children }) => {
  return <p dir="auto">{children}</p>;
};
