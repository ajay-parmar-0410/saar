import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ImpactBadge } from "./impact-badge";

describe("ImpactBadge", () => {
  it("renders HIGH impact text", () => {
    render(<ImpactBadge impact="HIGH" />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("renders MEDIUM impact text", () => {
    render(<ImpactBadge impact="MEDIUM" />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("renders LOW impact text", () => {
    render(<ImpactBadge impact="LOW" />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("applies HIGH styles", () => {
    render(<ImpactBadge impact="HIGH" />);
    const badge = screen.getByText("HIGH");
    expect(badge.className).toContain("destructive");
  });

  it("applies MEDIUM styles", () => {
    render(<ImpactBadge impact="MEDIUM" />);
    const badge = screen.getByText("MEDIUM");
    expect(badge.className).toContain("yellow");
  });

  it("applies LOW styles", () => {
    render(<ImpactBadge impact="LOW" />);
    const badge = screen.getByText("LOW");
    expect(badge.className).toContain("muted");
  });
});
