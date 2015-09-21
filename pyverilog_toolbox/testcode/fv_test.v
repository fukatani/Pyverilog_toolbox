module TOP(CLK);
  input CLK;
  reg A,B,C,D,E,F,G,H;
  reg [2:0] multi,multi2,I;

  always @(posedge CLK) begin
    A <= A || B;
    B <= 1'b0;
  end

  always @(posedge CLK) begin
    C <= !B;
  end

  always @(posedge CLK) begin
    D <= B == A;
  end

  always @(posedge CLK) begin
    E <= B ? A : C;
  end

  always @(posedge CLK) begin
    F <= &multi;
  end

  always @(posedge CLK) begin
    G <= &multi[1:0];
  end

  always @(posedge CLK) begin
    H <= F+G;
  end

  always @(posedge CLK) begin
    I <= multi & multi2;
  end

endmodule


