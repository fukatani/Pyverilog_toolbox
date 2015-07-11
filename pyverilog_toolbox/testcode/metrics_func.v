module TOP(CLK, RST, IN, IN2);
  input CLK, RST, IN, IN2;
  reg reg2;

/*
  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg2 <= 1'b0;
    end else if(IN2) begin
      reg2 <= IN;
    end else if(IN2) begin
      if(IN2) begin
        reg2 <= IN;
      end
    end else begin
      if({IN2, IN2}) begin
        case(IN2)
          2'b00: reg2 <= 1'b0;
          2'b11: reg2 <= 1'b1;
          default: begin
            if(IN2)
              reg2 <= IN;
            else
              reg2 <= func1(IN,IN2);
          end
        endcase
      end
    end
  end
*/

  always @(posedge CLK or negedge RST) begin
      reg2 <= func1(IN,IN2);
  end
  function func1;
    input bit;
    input bit2;

      if(bit2)
        func1 = !bit;
      else
        func1 = bit;

  endfunction

/*
  function func1;
    input bit;
    input bit2;

      case(bit2)
        'h0: begin
          func1 = !bit;
        end
        default: begin
          func1 = bit;
        end
      endcase
  endfunction
*/


endmodule

